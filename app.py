import os, math, json, io, requests, streamlit as st
from PIL import Image

# ============ NEW: vision imports ============
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration

# =========================
# Config
# =========================
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
MAX_CONTEXT_TOKENS = 7000
RESERVE_FOR_REPLY = 1000
KEEP_LAST_TURNS = 8

# =========================
# UI Setup
# =========================
st.set_page_config(page_title="Local Chat (Ollama) + Vision", page_icon="🖼️", layout="centered")
st.title("🖼️ Local Chat (Ollama) — Vision + Persona + Memory")

with st.sidebar:
    st.markdown("### Settings")
    model = st.text_input("Model", value=DEFAULT_MODEL, help="Pulled in Ollama, e.g. llama3.1:8b, mistral, etc.")
    st.caption(f"Ollama endpoint: {OLLAMA_URL}")

# Persona presets
PERSONAS = {
    "Neutral (default)": "",
    "Funny Sidekick": (
        "You are a witty sidekick. Always include a light, tasteful joke or pun related to the user’s topic. "
        "Be helpful first, funny second. Keep jokes one line."
    ),
    "Sports Commentator": (
        "You are a sports commentator. Frame all answers with play-by-play flair and sports metaphors. "
        "If the topic isn’t sports, still relate it to games, players, strategy, or scores."
    ),
    "Mystery Detective (Noir)": (
        "You are a noir detective. Speak in moody, first-person monologue. Use short, punchy lines. "
        "Investigate user queries like cases, laying out clues, suspects, and conclusions."
    ),
}

colA, colB = st.columns([2, 1])
with colA:
    persona_choice = st.selectbox("Persona Twist", list(PERSONAS.keys()))
with colB:
    stream_toggle = st.toggle("Stream reply", value=True)

custom_system = st.text_area(
    "Optional: Custom system prompt (overrides preset if not empty)",
    value="",
    height=80,
    placeholder="Write persona/behavior rules here…"
)

# ============ NEW: image URL input ============
st.markdown("### Image (optional)")
img_url = st.text_input("Paste an image URL (JPG/PNG/WebP). If provided, I will analyze it.")
# Preview slot
img_preview_slot = st.empty()

# =========================
# Session State
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "rolling_summary" not in st.session_state:
    st.session_state.rolling_summary = ""

# =========================
# Helpers: tokens, API, memory
# =========================
def estimate_tokens(text: str) -> int:
    if not text: return 0
    return max(1, math.ceil(len(text) / 4))

def count_message_tokens(msg) -> int:
    return estimate_tokens(msg.get("content", "")) + 4

def count_messages_tokens(msgs) -> int:
    return sum(count_message_tokens(m) for m in msgs)

def ollama_chat(messages, model_name: str, stream: bool = False, temperature: float = 0.7):
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": stream,
        "options": {"temperature": temperature}
    }
    if not stream:
        r = requests.post(OLLAMA_URL, json=payload, timeout=600)
        r.raise_for_status()
        return r.json()["message"]["content"]
    else:
        with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=600) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line:
                    continue
                data = json.loads(line)
                chunk = data.get("message", {}).get("content", "")
                yield chunk
                if data.get("done"):
                    break

def current_persona_system() -> str:
    preset = PERSONAS.get(persona_choice, "")
    return (custom_system.strip() or preset).strip()

def build_messages(persona_system: str, history: list, rolling_summary: str,
                   image_context: str = "",
                   max_context_tokens=MAX_CONTEXT_TOKENS, reserve_for_reply=RESERVE_FOR_REPLY):
    msgs = []
    if persona_system:
        msgs.append({"role": "system", "content": persona_system})
    if rolling_summary.strip():
        msgs.append({"role": "system", "content": f"CONTEXT SUMMARY (durable facts):\n{rolling_summary.strip()}"})
    if image_context.strip():
        # ============ NEW: inject image caption/features ============
        msgs.append({"role": "system", "content": f"IMAGE CONTEXT:\n{image_context.strip()}"})
    # Add tail of history within budget
    budget = max_context_tokens - reserve_for_reply - count_messages_tokens(msgs)
    tail = []
    for m in reversed(history):
        c = count_messages_tokens([m])
        if c <= budget:
            tail.append(m); budget -= c
        else:
            break
    msgs.extend(reversed(tail))
    return msgs

def summarize_history(history: list, current_summary: str) -> str:
    turns = []
    for m in history:
        if m["role"] in ("user", "assistant"):
            who = "User" if m["role"] == "user" else "Assistant"
            turns.append(f"{who}: {m['content']}")
    transcript = "\n".join(turns)
    sys = (
        "You are a concise note-taker. Summarize the conversation below into 10-15 bullet points.\n"
        "Keep ONLY durable facts: user goals, constraints, decisions, preferences, action items.\n"
        "Be neutral and compact. Exclude jokes and system/internal details."
    )
    msgs = [
        {"role": "system", "content": sys},
        {"role": "user", "content": f"Previous rolling summary (may be empty):\n{current_summary}\n\nConversation to summarize:\n{transcript}"}
    ]
    summary = ollama_chat(msgs, model, stream=False, temperature=0.0)
    return summary.strip()

def maintain_memory(persona_system: str,
                    max_context_tokens=MAX_CONTEXT_TOKENS,
                    reserve_for_reply=RESERVE_FOR_REPLY,
                    keep_last_turns=KEEP_LAST_TURNS):
    msgs = build_messages(
        persona_system,
        st.session_state.messages,
        st.session_state.rolling_summary,
        image_context="",  # memory check independent of current image
        max_context_tokens=max_context_tokens,
        reserve_for_reply=reserve_for_reply,
    )
    if count_messages_tokens(msgs) > (max_context_tokens - reserve_for_reply):
        new_summary = summarize_history(st.session_state.messages, st.session_state.rolling_summary)
        st.session_state.rolling_summary = new_summary
        st.session_state.messages = st.session_state.messages[-keep_last_turns:]

# ============ NEW: BLIP captioner (cached) ============
@st.cache_resource(show_spinner=False)
def load_blip():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model_ = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)
    return processor, model_, device

def generate_image_caption_from_url(url: str) -> tuple[str, Image.Image]:
    """Downloads image and returns (caption, PIL.Image). Raises on error."""
    resp = requests.get(url, stream=True, timeout=20)
    resp.raise_for_status()
    img = Image.open(io.BytesIO(resp.content)).convert("RGB")
    processor, model_, device = load_blip()
    inputs = processor(images=img, return_tensors="pt").to(device)
    out = model_.generate(**inputs, max_new_tokens=60)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption.strip(), img

# =========================
# Render prior history
# =========================
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# =========================
# Input & Response
# =========================
prompt = st.chat_input("Type your message… (optionally add an image URL above)")
if prompt:
    # Save and render the user message immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # If image URL provided, fetch + caption + show preview
    image_context = ""
    if img_url.strip():
        try:
            with st.spinner("Downloading & analyzing image…"):
                caption, preview = generate_image_caption_from_url(img_url.strip())
            img_preview_slot.image(preview, caption=f"Image from URL — Caption: {caption}", use_container_width=True)
            # Provide the LLM with a compact, useful context
            image_context = f"URL: {img_url}\nCaption: {caption}"
        except Exception as e:
            st.warning(f"Image analysis failed: {e}")

    # Maintain memory and build final prompt (inject image context)
    persona_system = current_persona_system()
    maintain_memory(persona_system)
    final_messages = build_messages(
        persona_system,
        st.session_state.messages,
        st.session_state.rolling_summary,
        image_context=image_context,  # << NEW
        max_context_tokens=MAX_CONTEXT_TOKENS,
        reserve_for_reply=RESERVE_FOR_REPLY
    )

    # Generate assistant reply
    with st.chat_message("assistant"):
        if stream_toggle:
            placeholder, full = st.empty(), ""
            for delta in ollama_chat(final_messages, model, stream=True):
                full += delta
                placeholder.markdown(full)
        else:
            full = ollama_chat(final_messages, model, stream=False)
            st.markdown(full)

    # Save assistant reply
    st.session_state.messages.append({"role": "assistant", "content": full})

# =========================
# Footer / Debug
# =========================
with st.expander("🔎 Debug / Context Info"):
    st.write("Rolling summary (internal):")
    st.code(st.session_state.rolling_summary or "(empty)", language="markdown")
    persona_preview = current_persona_system() or "(none)"
    st.write("Active system prompt:")
    st.code(persona_preview, language="markdown")
