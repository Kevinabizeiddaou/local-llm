# 🧠 Local Chat with Ollama + Streamlit

A lightweight, privacy-first chatbot that runs **entirely on your machine** using open-source transformer models from **[Ollama](https://ollama.com/)**.  
It supports **personas (“Twists”)**, **memory summarization**, **image understanding**, and **prompt-engineering** for realistic, context-aware conversations.

## ⚙️ 1. Setup Instructions

### **Requirements**

- Python 3.9 or newer
- Ollama installed and running locally
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh     # macOS/Linux
  ```
  or download the Windows installer from [ollama.com](https://ollama.com/download).

### **Model Download**

You can use any Ollama model. Example:

```bash
ollama pull llama3.1:8b
```

### **Python Dependencies**

```bash
pip install streamlit requests torch torchvision transformers timm pillow
```

### **Run the App**

```bash
python -m streamlit run app.py
```

Once running, open the provided local URL (usually `http://localhost:8501`).

---

## 💬 2. Usage Guide

1. **Choose a Persona (“Twist”)** from the dropdown (e.g., Funny Sidekick, Sports Commentator, Mystery Detective).
2. Optionally, **write your own custom system prompt** to fully define the bot’s personality and behavior.
3. Type a message and hit Enter.
   - Your message and the assistant’s reply appear instantly.
   - Older messages are summarized automatically to maintain long-term context.
4. Paste an **image URL** if you want the bot to analyze it.
   - The app will **download the image**, run a **BLIP captioning model**, and feed the generated description into the LLM context.
5. Check the **Debug / Context Info** section to view the active system prompt and rolling summary.

---

## 🧠 3. Image Processing & Vision Integration

This app integrates a **BLIP (Bootstrapped Language Image Pretraining)** model to caption images and pass their descriptions to the LLM.

### Workflow:

1. User pastes an image URL.
2. The app downloads the image via `requests`.
3. BLIP generates a textual caption (e.g., “a man wearing a blue jacket walking in a park”).
4. This caption is appended as a **system message** under `IMAGE CONTEXT`.
5. The LLM incorporates it when forming a response.

### Example Prompts:

| User Prompt                           | Image Context                         | Bot Behavior                          |
| ------------------------------------- | ------------------------------------- | ------------------------------------- |
| “What outfit is this person wearing?” | Caption describes clothing            | Bot answers based on detected outfit  |
| “Describe the mood of this scene.”    | Caption mentions expressions, setting | Bot responds emotionally/artistically |

---

## 🧩 4. Model Details

- **Default Text Model:** `llama3.1:8b`
- **Vision Model:** `Salesforce/blip-image-captioning-base`
- **Context Window:** 8,192 tokens
- **API:** Served locally via `http://localhost:11434/api/chat`
- **Architecture:** Streamlit frontend → BLIP captioner → Ollama backend

---

## 🎭 5. Persona “Twist” Implementation

Each **Twist** is implemented as a **system prompt** prepended to every conversation.  
This defines how the model should “act,” shaping its tone and response structure.

| Persona                      | System Prompt Summary                                                 |
| ---------------------------- | --------------------------------------------------------------------- |
| **Funny Sidekick**           | “Be a witty helper. Always include one short joke or pun.”            |
| **Sports Commentator**       | “Talk like a play-by-play announcer. Use sports metaphors.”           |
| **Mystery Detective (Noir)** | “Speak in moody, first-person monologue. Treat questions like clues.” |

You can add your own by writing any prompt in the “Custom system prompt” box — it overrides presets.

---

## 🧱 6. Prompt-Engineering Techniques

| Technique                   | Description                                                | Implementation                                                       |
| --------------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------- |
| **System Prompts**          | Define tone, role, and constraints.                        | First message in `messages[]` (system role).                         |
| **Context Summarization**   | Keeps conversation memory under the model’s context limit. | `summarize_history()` compresses older turns into a rolling summary. |
| **Image Context Injection** | Adds BLIP-generated captions to chat context.              | Added as `IMAGE CONTEXT` system message.                             |
| **Token Budgeting**         | Ensures context + reply fit in the model’s window.         | Tracks estimated tokens and truncates if needed.                     |
| **Recency Priority**        | Keeps the latest N turns verbatim for short-term memory.   | `KEEP_LAST_TURNS` parameter.                                         |
| **Streaming Responses**     | Displays model output in real-time for responsiveness.     | `stream=True` mode with incremental rendering.                       |

---

## 🧩 7. Example Prompts

**Funny Sidekick:**

> You: Explain neural networks  
> Bot: Sure! They’re like brainy spaghetti — lots of tangled connections passing signals until you get a tasty output 😄

**Sports Commentator:**

> You: Summarize AI ethics  
> Bot: It’s a tight match between innovation and responsibility! On one side, progress sprints ahead; on the other, fairness plays solid defense.

**Mystery Detective:**

> You: Describe data privacy  
> Bot: The case was simple. Too much data in the wrong hands. I followed the trail — encryption, consent, accountability. The usual suspects.

**Image-Aware Example:**

> You: What mood does this picture convey?  
> _(paste an image URL of a rainy city street)_  
> Bot: The streetlights flicker off wet asphalt — lonely yet alive, like the city’s heartbeat on a sleepless night.

---

## ⚙️ 8. Configuration Options

You can modify in `app.py`:

| Variable             | Purpose                              | Default                           |
| -------------------- | ------------------------------------ | --------------------------------- |
| `MAX_CONTEXT_TOKENS` | Context budget before summarizing    | 7000                              |
| `KEEP_LAST_TURNS`    | Number of recent turns kept verbatim | 8                                 |
| `OLLAMA_URL`         | Backend endpoint                     | `http://localhost:11434/api/chat` |
| `MODEL`              | Active model name                    | `llama3.1:8b`                     |

---

## 🧾 9. Future Enhancements

- Download/export chat history
- Add dark/light theme toggle
- Support voice input (SpeechRecognition)
- Multi-persona memory per session
- CLIP-based image embeddings for deeper visual reasoning

---

## 🧑‍💻 Author

Created by **Kevin Abi Zeid Daou** — AUB Software Engineering Student (AI Track).  
This project demonstrates **prompt engineering**, **vision-language integration**, **context management**, and **local transformer deployment** using **Ollama + Streamlit**.
