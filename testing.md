# 🧪 Testing Guide

This project includes a full testing workflow for validating all major components before submission or deployment.

---

# Before You Start

Make sure your local environment is ready.

Verify these three prerequisites:

* Ollama is running in the background
* Required models are installed
* `.env` file contains valid Telegram and Discord tokens

Run:

```bash
ollama pull llama3
ollama pull llava
```

---

# Phase 1 — Local UI (Gradio)

Testing locally first is recommended because it verifies the core engines without involving Telegram or Discord APIs.

## Start

```bash
python local_ui.py
```

Open:

```text
http://127.0.0.1:7860
```

---

## Test Direct Retrieval

Ask:

```text
What is the guest Wi-Fi password?
```

Expected result:

* Connect to `Corp_Guest`
* Password `Welcome2024!`

---

## Test Memory / History

Ask:

```text
I have an IT emergency. Who should I contact?
```

Expected:

```text
Mike Chen
```

Then ask:

```text
What is his phone number?
```

Expected:

```text
555-0198
```

---

## Test Summarizer

Action:

Click:

```text
Run /summarize
```

Expected:

A short summary of recent interactions.

---

## Test Vision

Switch to the Vision tab.

Upload any image.

Click:

```text
Analyze Image
```

Expected:

* one sentence caption
* exactly 3 hashtags

---

# Phase 2 — Telegram Bot

## Start

Stop Gradio first, then run:

```bash
python main.py
```

Open Telegram and locate your bot.

---

## Test Start Menu

Send:

```text
/start
```

Expected:

Welcome menu appears.

---

## Test Complex RAG

Send:

```text
/ask I am a new remote employee. How much is the home office stipend and what can I buy with it?
```

Expected:

* answer includes `$500`
* mentions desks, chairs, monitors
* source reference appended

---

## Test Cache System

Send:

```text
/ask What is the guest Wi-Fi password?
```

Expected first time:

* few seconds delay

Send same query again.

Expected second time:

* instant reply
* cached prefix visible

---

## Test Image Upload

Send image directly (no command).

Expected:

* acknowledgement message
* caption generated
* tags returned

---

# Phase 3 — Discord Bot

Bot is already active because `main.py` runs both platforms.

Open your Discord server.

---

## Test RAG Logic

Send:

```text
/ask If I take 3 sick days, do I need a doctor's note?
```

Expected:

Answer explains doctor's note rule.

---

## Test Cross-Platform Isolation

Send:

```text
/summarize
```

Expected:

Only Discord conversation is summarized.

Telegram history must not appear.

---

## Test Discord Image Command

Send:

```text
/image
```

Attach an image before sending.

Expected:

* image processed
* temporary file deleted
* caption + tags returned

---

# Success Criteria

If all three phases pass:

✅ RAG works
✅ Vision works
✅ Memory works
✅ Cache works
✅ Telegram works
✅ Discord works

Project is fully validated.