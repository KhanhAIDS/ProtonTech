# AI Email Summarizer

A lightweight Python CLI tool that uses OpenAI's API to analyze and summarize emails. It extracts key information and outputs a structured JSON response containing a brief summary, action items, priority level, and people mentioned.

## Features
- **Flexible Input:** Read email content directly from the command line or from a `.txt` file.
- **Structured Output:** Enforces a strict JSON format using OpenAI's `json_object` response format.
- **Error Handling:** Built-in exception handling for API timeouts and JSON parsing errors.

## Prerequisites
- Python 3.7+
- An OpenAI API Key

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-github-repo-url>
   cd 8_5_2026
   ```

2. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up your environment variables:**
   Create a `.env` file in the root directory and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

You can run the script using either direct text or a file path.

**Option 1: Pass text directly**

```bash
python mini_prj_1_AI_email_summarizer.py --text "Hi team, the project is delayed. David, please check the logs immediately. We need this fixed by 5 PM."

```

**Option 2: Read from a file**

```bash
python mini_prj_1_AI_email_summarizer.py --file data/email_1_urgent.txt

```

## Expected Output

The script will return a formatted JSON object:

```json
{
    "summary": "The project is currently experiencing delays and requires immediate attention.",
    "action_items": [
        "Check the logs immediately",
        "Fix the issue by 5 PM"
    ],
    "priority": "High",
    "people_mentioned": [
        "David"
    ]
}

```

## Project Structure

```text
8_5_2026/
├── data/                                 # Folder containing sample email text files
├── mini_prj_1_AI_email_summarizer.py     # Main application script
├── requirements.txt                      # Project dependencies
├── .env.example                          # Template for environment variables
└── README.md                             # Project documentation

```