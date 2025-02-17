# Ctrl_Shift_Intelligence

## Overview
This project leverages **Groq** and **DeepSeek-R1-LLaMA-70B** to create an advanced **LLM-powered Chess Coach**. The model integrates **Stockfish**, one of the strongest chess engines, to analyze board positions and recommend the best moves while providing insightful explanations.

## Features
- **LLM Integration**: Uses **DeepSeek-R1-LLaMA-70B** via **Groq** to generate human-like explanations for chess moves.
- **Stockfish Analysis**: Evaluates board positions and suggests the optimal move.
- **Move Justification**: Provides detailed reasoning behind Stockfish's suggested move.
- **User Interaction**: Allows users to input their board position and receive AI-driven coaching.
- **Real-time Feedback**: Ensures prompt and accurate move recommendations.

## Tech Stack
- **LLM Backend**: [Groq](https://groq.com/) with **DeepSeek-R1-LLaMA-70B**.
- **Chess Engine**: [Stockfish](https://stockfishchess.org/).
- **Frameworks & Tools**:
  - Python
  - Flask / FastAPI (for API development)
  - Chess libraries (e.g., `python-chess`)

## Installation
1. **Clone the Repository:**
   ```sh
   git clone https://github.com/RudranilJadhav/Ctrl_Shift_Intelligence.git
   cd Ctrl_Shift_Intelligence
   ```
2. **Create a Virtual Environment (Optional but Recommended):**
   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Download and Install Stockfish:**
   - Visit [Stockfish Download Page](https://stockfishchess.org/download/) and install the appropriate version.
   - Ensure Stockfish is accessible from the command line.
5. **Set Up API Keys (if required for Groq access).**

## Usage
to be filled

## Roadmap
- **Enhancing explanations with LLM fine-tuning on chess commentary data.**
- **Adding multi-variant move analysis.**
- **Integrating a web-based UI for better usability.**

## Contributing
Contributions are welcome! Feel free to open an issue or submit a pull request.

## License
This project is licensed under the MIT License.

## Acknowledgments
- **Stockfish Team** for their exceptional chess engine.
- **Groq & DeepSeek** for enabling high-performance LLM inference.
- The **open-source chess community** for invaluable libraries and tools.
