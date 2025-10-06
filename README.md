# 🧠 Local Chat with Ollama + Streamlit

A lightweight, privacy-first chatbot that runs **entirely on your machine** using open-source transformer models from **[Ollama](https://ollama.com/)**.  
It supports **personas (“Twists”)**, **memory summarization**, and **prompt-engineering** for realistic, context-aware conversations.

---

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
pip install streamlit requests
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
4. Check the **Debug / Context Info** section to view the active system prompt and rolling summary.

---

## 🧩 3. Model Details

- **Default Model:** `llama3.1:8b` (meta’s Llama 3.1, 8B parameters)
- **Context Window:** 8,192 tokens
- **API:** Served locally via `http://localhost:11434/api/chat`
- **Architecture:** Streamlit frontend → local Ollama HTTP backend

You can switch to other models by changing the “Model” field in the sidebar or setting an environment variable:

```bash
export OLLAMA_MODEL="mistral"
```

---

## 🎭 4. Persona “Twist” Implementation

Each **Twist** is implemented as a **system prompt** prepended to every conversation.  
This defines how the model should “act,” shaping its tone and response structure.  
Example snippets:

| Persona                      | System Prompt Summary                                                 |
| ---------------------------- | --------------------------------------------------------------------- |
| **Funny Sidekick**           | “Be a witty helper. Always include one short joke or pun.”            |
| **Sports Commentator**       | “Talk like a play-by-play announcer. Use sports metaphors.”           |
| **Mystery Detective (Noir)** | “Speak in moody, first-person monologue. Treat questions like clues.” |

You can add your own by writing any prompt in the “Custom system prompt” box — it overrides presets.

---

## 🧱 5. Prompt-Engineering Techniques

| Technique                 | Description                                                | Implementation                                                       |
| ------------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------- |
| **System Prompts**        | Define tone, role, and constraints.                        | First message in `messages[]` (system role).                         |
| **Context Summarization** | Keeps conversation memory under the model’s context limit. | `summarize_history()` compresses older turns into a rolling summary. |
| **Token Budgeting**       | Ensures context + reply fit in the model’s window.         | Tracks estimated tokens and truncates if needed.                     |
| **Recency Priority**      | Keeps the latest N turns verbatim for short-term memory.   | `KEEP_LAST_TURNS` parameter.                                         |
| **Streaming Responses**   | Displays model output in real-time for responsiveness.     | `stream=True` mode with incremental rendering.                       |

---

## 🧩 6. Example Prompts

**Funny Sidekick:**

> You: Explain neural networks
>
> Bot: Sure! They’re like brainy spaghetti — lots of tangled connections passing signals until you get a tasty output 😄

**Sports Commentator:**

> You: Summarize AI ethics
>
> Bot: It’s a tight match between innovation and responsibility! On one side, progress sprints ahead; on the other, fairness plays solid defense.

**Mystery Detective:**

> You: Describe data privacy
>
> Bot: The case was simple. Too much data in the wrong hands. I followed the trail — encryption, consent, accountability. The usual suspects.

---

## 🧰 7. Configuration Options

You can modify in `app.py`:
| Variable | Purpose | Default |
|-----------|----------|---------|
| `MAX_CONTEXT_TOKENS` | Context budget before summarizing | 7000 |
| `KEEP_LAST_TURNS` | Number of recent turns kept verbatim | 8 |
| `OLLAMA_URL` | Backend endpoint | `http://localhost:11434/api/chat` |
| `MODEL` | Active model name | `llama3.1:8b` |

---

## 🧾 8. Future Enhancements

- Download/export chat history
- Add dark/light theme toggle
- Support voice input (SpeechRecognition)
- Multi-persona memory per session

---

## 🧑‍💻 Author

Created by **Kevin Abi Zeid Daou** — AUB Software Engineering Student (AI Track).  
This project demonstrates **prompt engineering**, **context management**, and **local transformer deployment** using **Ollama + Streamlit**.
