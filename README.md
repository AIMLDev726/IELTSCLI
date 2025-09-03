# IELTS Practice CLI 🎯

A powerful command-line tool for IELTS writing practice with intelligent assessment and detailed feedback.

## 🌟 What This Tool Does

This application helps IELTS candidates practice writing tasks by:
- Generating realistic IELTS prompts
- Providing detailed band score assessments
- Tracking progress over multiple sessions
- Offering specific improvement suggestions

Perfect for students preparing for IELTS Academic and General Training writing modules.

## 📋 Requirements

- Python 3.8 or higher
- An API key from one of these providers:
  - **OpenAI** (recommended for best results)
  - **Google AI** (Gemini models)
  - **Ollama** (for local/offline use)

## 🚀 Quick Setup

### Step 1: Download and Install

```bash
# Download the project
git clone https://github.com/AIMLDev726/IELTSCLI.git
cd IELTSCLI

# Install required packages
pip install -r requirements.txt
```

### Step 2: Get an API Key

**Option A: OpenAI (Recommended)**
1. Go to [OpenAI Platform](https://platform.openai.com)
2. Create an account or sign in
3. Navigate to "API Keys" section
4. Create a new API key
5. Copy the key (starts with `sk-`)

**Option B: Google AI**
1. Visit [Google AI Studio](https://makersuite.google.com)
2. Sign in with your Google account
3. Click "Get API Key"
4. Create a new API key
5. Copy the key

**Option C: Local Setup (Ollama)**
1. Install [Ollama](https://ollama.ai)
2. Run: `ollama pull llama2`
3. No API key needed

### Step 3: First Run

```bash
python main.py
```

The application will guide you through the initial setup.

## 📚 How to Use

### Starting Your First Practice Session

```bash
# Start a Writing Task 2 practice
python main.py practice --type writing_task_2
```

### During Practice

1. **Read the prompt** carefully
2. **Write your response** (minimum 250 words for Task 2)
3. **Type `SUBMIT`** on a new line when finished
4. **Review your assessment** with band scores and feedback

### Example Session

```
$ python main.py practice --type writing_task_2

📋 Task Prompt:
Some people believe that technology is making traditional teachers less important 
in education. Others argue that teachers are more crucial than ever.

Discuss both views and give your opinion.
Write at least 250 words.

Your response:
Technology has transformed many aspects of our lives, including education...

[Continue writing your essay]

SUBMIT

🎯 Assessment Results:
Overall Band Score: 6.5

Task Achievement: 7.0
- Clear position with relevant examples
- Well-developed response to the prompt

Coherence and Cohesion: 6.0
- Good paragraph structure
- Could use more linking words

[Detailed feedback continues...]
```

## 🎯 Features

### ✅ What You Get

- **Realistic IELTS prompts** generated specifically for your practice
- **Detailed band scores** for all four assessment criteria
- **Specific feedback** on what to improve
- **Progress tracking** across multiple sessions
- **Word count monitoring** during writing
- **Time tracking** to simulate exam conditions

### 📊 Assessment Criteria

The tool evaluates your writing based on official IELTS criteria:

**Writing Task 2:**
- Task Response (25%)
- Coherence and Cohesion (25%) 
- Lexical Resource (25%)
- Grammatical Range and Accuracy (25%)

**Writing Task 1:**
- Task Achievement (25%)
- Coherence and Cohesion (25%)
- Lexical Resource (25%)
- Grammatical Range and Accuracy (25%)

## 📖 Commands Reference

### Basic Commands

```bash
# Start practice session
python main.py practice --type writing_task_2

# View recent sessions
python main.py sessions

# Check configuration
python main.py config --show

# Test API connection
python main.py test
```

### Advanced Options

```bash
# Practice with time limit
python main.py practice --type writing_task_2 --time 40

# Quick practice (no assessment)
python main.py practice --quick

# Resume previous session
python main.py practice --resume SESSION_ID

# Export session data
python main.py sessions --export my_sessions.json

# View detailed statistics
python main.py stats --detailed
```

## 🔧 Configuration

### Change AI Provider

```bash
# Switch to OpenAI
python main.py config --provider openai --api-key YOUR_KEY

# Switch to Google AI
python main.py config --provider google --api-key YOUR_KEY

# Switch to local Ollama
python main.py config --provider ollama
```

### Customize Settings

```bash
# Set default task type
python main.py config --set task_type --value writing_task_2

# Enable detailed feedback
python main.py config --set show_detailed_feedback --value true

# Set default time limit
python main.py config --set default_time_limit --value 40
```

## 🗂️ Project Structure

```
IELTSCLI/
├── src/
│   ├── cli/                 # User interface components
│   ├── core/                # Core application logic
│   ├── llm/                 # AI provider integration
│   ├── assessment/          # IELTS scoring engine
│   ├── storage/             # Data management
│   └── utils/               # Helper functions
├── docs/                    # Documentation
├── tests/                   # Test files
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
└── setup.py                # Installation configuration
```

## 🛠️ Troubleshooting

### Common Issues

**"No API key configured"**
```bash
python main.py config --provider openai --api-key YOUR_KEY
```

**"Connection failed"**
```bash
python main.py test --connection
```

**"Import errors"**
```bash
pip install -r requirements.txt
```

**"Permission denied"**
- Run terminal as administrator (Windows)
- Use `sudo` if needed (Mac/Linux)

### Getting Help

```bash
# General help
python main.py --help

# Command-specific help
python main.py practice --help
python main.py config --help
```

## 📊 Example Band Scores

Here's what different performance levels look like:

**Band 8-9 (Excellent)**
- Clear, well-developed arguments
- Wide range of vocabulary
- Complex sentence structures
- Minimal errors

**Band 6-7 (Good)**
- Clear position with examples
- Good vocabulary range
- Mix of simple and complex sentences
- Some minor errors

**Band 4-5 (Needs Work)**
- Basic task response
- Limited vocabulary
- Simple sentences mostly
- Frequent errors affecting meaning

## 🤝 Contributing

We welcome contributions! Here's how to help:

1. Fork this repository
2. Create a new branch for your feature
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source under the MIT License.

## 📞 Support

- **Email**: aistudentlearn4@gmail.com
- **GitHub Issues**: [Report problems here](https://github.com/AIMLDev726/IELTSCLI/issues)
- **Documentation**: Check the `docs/` folder for detailed guides

---

**Start practicing today and improve your IELTS writing scores! 🎯**
