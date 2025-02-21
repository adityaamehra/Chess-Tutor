# Chess Tutor AI

### 🏆 A Multi-Page Chess Tutor AI Powered by DeepSeek-R1-LLaMA-70B, Stockfish, and Streamlit

---

## 📌 Overview
Chess Tutor AI is an interactive and intelligent chess tutor designed to help users improve their chess skills. It leverages **DeepSeek-R1-LLaMA-70B** for advanced reasoning, the **Groq API** for processing, and the **Stockfish API** for best move evaluation. The project is built using **Streamlit**, providing a seamless and engaging web interface.

## 🚀 Features
### 1️⃣ Chess Bot
- 📌 **Best Move Analysis**: Provides the best move along with an in-depth explanation when given an **FEN** string.
- 📌 **Opening Theory**: Offers insights into chess openings, including their **pros, cons, and major variations**.
- 📌 **Strategic Insights**: Explains why a move is optimal and suggests alternative approaches.

### 2️⃣ Chess Puzzles
- 📌 **Difficulty Levels**: Puzzles categorized into **Easy, Medium, and Hard**, selected at random.
- 📌 **Interactive UI**: Buttons for **Get Hint**, **Submit Move**, and **Next Puzzle**.
- 📌 **Board Visualization**: Implemented using **SVG images** for clarity and better understanding.

### 3️⃣ Human vs. AI Mode
- 📌 **Adjustable AI Strength**: Modify **Stockfish depth** to customize difficulty.
- 📌 **AI Move Automation**: The AI automatically responds to each human move.
- 📌 **Move Assessment**: Detailed breakdown in a **three-column layout**:
  - **AI Move Explanation** 🧠
  - **User Move Evaluation** 📊
  - **Best Possible Continuation** ♟️

## 🛠️ Technologies Used
- **DeepSeek-R1-LLaMA-70B** - For chess reasoning and explanations
- **Groq API** - For AI model inference
- **Stockfish API** - For move evaluation and analysis
- **Streamlit** - For building the interactive web UI
- **SVG Rendering** - For board visualization

## 🏁 Installation & Setup
1. **Clone the Repository**
   ```bash
   git clone https://github.com/adityaamehra/Chess-Tutor.git
   cd Chess-Tutor
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   streamlit run main.py
   ```

## 🤝 Contributions
Contributions are welcome! Feel free to open issues and submit pull requests.

## 📜 License
This project is licensed under the MIT License.

---

🎯 **Level up your chess skills with AI-powered insights!** 🏆
