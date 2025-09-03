# Getting Started with IELTS Practice CLI

This guide will help you set up and start using the IELTS Practice CLI tool step by step.

## Prerequisites

Before you begin, make sure you have:
- Python 3.8 or higher installed on your computer
- Basic familiarity with using the command line/terminal
- An internet connection (for AI assessment features)

## Installation Steps

### Step 1: Download the Project

**Option A: Using Git (Recommended)**
```bash
git clone https://github.com/AIMLDev726/IELTSCLI.git
cd IELTSCLI
```

**Option B: Download ZIP**
1. Go to https://github.com/AIMLDev726/IELTSCLI
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Open terminal/command prompt in the extracted folder

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

If you encounter permission errors on Windows, try:
```bash
pip install --user -r requirements.txt
```

On Mac/Linux, you might need:
```bash
pip3 install -r requirements.txt
```

### Step 3: Get an AI API Key

You need an API key from one of these providers:

#### Option A: OpenAI (Recommended)
1. Visit https://platform.openai.com
2. Sign up or log in
3. Go to "API Keys" in the left menu
4. Click "Create new secret key"
5. Copy the key (it looks like: `sk-...`)
6. **Important**: Store this key safely - you cannot see it again

#### Option B: Google AI (Alternative)
1. Go to https://makersuite.google.com
2. Sign in with your Google account
3. Click "Get API Key"
4. Create a new API key
5. Copy the key

#### Option C: Local Setup (No API Key Needed)
1. Install Ollama from https://ollama.ai
2. Run: `ollama pull llama2`
3. This runs everything locally on your computer

## Initial Setup

### First Run

```bash
python main.py
```

The application will ask you to configure it. Here's what to do:

1. **Choose your AI provider**:
   - Type `1` for OpenAI (best results)
   - Type `2` for Google AI  
   - Type `3` for Ollama (local)

2. **Enter your API key** (skip for Ollama):
   - Paste the API key you copied earlier
   - The application will test the connection

3. **Set preferences**:
   - Choose your default task type (recommend: Writing Task 2)
   - Enable detailed feedback (recommended: Yes)

## Your First Practice Session

### Starting Practice

```bash
python main.py practice --type writing_task_2
```

### What Happens Next

1. **You'll see a prompt** like this:
   ```
   Some people believe that technology is making traditional teachers 
   less important in education. Others argue that teachers are more 
   crucial than ever.
   
   Discuss both views and give your opinion.
   Write at least 250 words.
   ```

2. **Start writing your response**:
   - The application will show live word count
   - You'll see time elapsed
   - Write naturally - the tool tracks everything

3. **When finished, type `SUBMIT`** on a new line

4. **Review your assessment**:
   - Overall band score
   - Detailed breakdown for each criterion
   - Specific suggestions for improvement

### Example Writing Session

```
Your response:
Technology has undoubtedly transformed education in numerous ways...

[Continue writing your essay here]

In conclusion, while technology provides valuable tools, teachers 
remain essential for guiding students through complex learning 
processes and developing critical thinking skills.

SUBMIT
```

## Understanding Your Results

### Band Scores
- **9.0**: Expert level
- **8.0-8.5**: Very good
- **7.0-7.5**: Good (often sufficient for university)
- **6.0-6.5**: Competent 
- **5.0-5.5**: Modest
- **Below 5.0**: Needs significant improvement

### Assessment Criteria

**Task Response (25%)**
- Did you answer the question completely?
- Is your position clear?
- Are your ideas well-developed?

**Coherence and Cohesion (25%)**
- Is your writing well-organized?
- Do paragraphs flow logically?
- Are linking words used effectively?

**Lexical Resource (25%)**
- Range of vocabulary used
- Accuracy of word choice
- Spelling accuracy

**Grammatical Range and Accuracy (25%)**
- Variety of sentence structures
- Grammar accuracy
- Punctuation usage

## Common Commands

### Basic Usage
```bash
# Start any practice session
python main.py practice

# Specific task type
python main.py practice --type writing_task_2

# With time limit (in minutes)
python main.py practice --type writing_task_2 --time 40

# Quick practice (no assessment)
python main.py practice --quick
```

### Managing Sessions
```bash
# View your recent sessions
python main.py sessions

# See detailed session info
python main.py sessions --details SESSION_ID

# Export your data
python main.py sessions --export my_sessions.json
```

### Configuration
```bash
# View current settings
python main.py config --show

# Change AI provider
python main.py config --provider openai --api-key YOUR_NEW_KEY

# Test your connection
python main.py test
```

## Tips for Better Results

### Writing Tips
1. **Plan before writing**: Spend 2-3 minutes planning your response
2. **Check word count**: Aim for 250-300 words for Task 2
3. **Time management**: Practice finishing within 40 minutes
4. **Review before submitting**: Check for obvious errors

### Using the Tool
1. **Practice regularly**: Consistent practice helps more than occasional long sessions
2. **Review feedback carefully**: Focus on the specific suggestions
3. **Track progress**: Use the stats command to see improvement over time
4. **Experiment with different topics**: Try various prompt types

## Troubleshooting

### "Command not found" errors
Make sure you're in the IELTSCLI folder:
```bash
cd path/to/IELTSCLI
python main.py
```

### "No module named..." errors
Reinstall dependencies:
```bash
pip install -r requirements.txt
```

### API connection problems
Test your connection:
```bash
python main.py test --connection
```

### General issues
Get help:
```bash
python main.py --help
```

## Next Steps

Once you're comfortable with basic usage:
1. Read the [User Guide](USER_GUIDE.md) for advanced features
2. Check [Examples](EXAMPLES.md) for sample responses and assessments
3. Review [Configuration Guide](CONFIGURATION.md) for customization options

## Getting Help

- **Email**: aistudentlearn4@gmail.com
- **GitHub Issues**: https://github.com/AIMLDev726/IELTSCLI/issues
- **Documentation**: Check other files in the `docs/` folder

Start practicing and improve your IELTS writing scores! 🎯
