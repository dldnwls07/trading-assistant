# 🚀 Google GenAI SDK Migration Plan

> **Note**: This document outlines the steps required to migrate from the deprecated `google.generativeai` package to the new `google.genai` SDK.
> **Date**: 2026-02-19
> **Status**: Planned (Future Work)

## 🎯 Objective
Migrate the project's AI integration code to use the latest `google.genai` SDK, ensuring long-term maintainability and access to new features, as support for `google.generativeai` has ended.

## 📦 Prerequisites
- Install the new SDK:
  ```bash
  pip install google-genai
  ```
- Reference Documentation: [Google GenAI Python SDK](https://github.com/googleapis/python-genai)

## 📂 Impacted Files
- `src/agents/ai_analyzer.py`: Main integration point for Gemini API.

## 📝 Migration Steps

### 1. Update Imports
Replace the deprecated import with the new one.

**Old (`google.generativeai`):**
```python
import google.generativeai as genai
```

**New (`google.genai`):**
```python
from google import genai
from google.genai import types
```

### 2. Update Client Initialization
Switch from global configuration to client-based usage.

**Old:**
```python
genai.configure(api_key=self.gemini_key)
self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
```

**New:**
```python
self.client = genai.Client(api_key=self.gemini_key)
# Model name is now passed directly during generation call or client config
```

### 3. Update Generation Calls (Text only)
The method signature for generating content has changed.

**Old:**
```python
response = self.gemini_model.generate_content(
    [prompt],
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json"
    )
)
result_json = json.loads(response.text)
```

**New:**
```python
response = self.client.models.generate_content(
    model='gemini-2.0-flash',
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json"
    )
)
result_json = json.loads(response.text)
```

### 4. Update Generation Calls (With Images)
Handling image inputs (multimodal) requires a different structure.

**Old:**
```python
content = [prompt]
if image_bytes:
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    content.append({
        "inline_data": {
            "mime_type": "image/png",
            "data": base64_image
        }
    })

response = self.gemini_model.generate_content(content, ...)
```

**New:**
```python
contents = [prompt]
if image_bytes:
    # Check if direct bytes or PIL image is supported, or encode as Part
    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    contents.append(image_part)

response = self.client.models.generate_content(
    model='gemini-2.0-flash',
    contents=contents,
    ...
)
```

### 5. Error Handling & Quotas
- Retain existing error handling (try-except blocks).
- Ensure 429 (Resource Exhausted) errors are caught to trigger the Groq fallback mechanism.
- The new SDK may raise `google.genai.errors.ClientError` or similar exceptions; check documentation for specific error classes.

## ✅ Verification Checklist
- [ ] `pip install google-genai` executed.
- [ ] `src/agents/ai_analyzer.py` refactored.
- [ ] Application starts without import errors.
- [ ] Text-only analysis (Gemini) works correctly.
- [ ] Image-based analysis (Gemini Vision) works correctly (if applicable).
- [ ] JSON parsing of the response works as expected.
- [ ] Fallback to Groq still functions when Gemini quota is exceeded.

## 🗓️ Execution Plan
This migration can be scheduled for the next maintenance window. The current deprecated SDK will continue to function for a short period, but migration is strongly recommended to receive updates and fixes.
