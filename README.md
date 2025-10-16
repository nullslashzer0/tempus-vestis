# 🧳 Tempus Vestis - AI-Powered Wardrobe Consultant

> _"Time and Dress"_ - Your intelligent packing assistant for weather-based wardrobe recommendations

Tempus Vestis is an AI-powered application that helps you determine what to pack for any trip. Using a sophisticated multi-agent system with dynamic tool selection and retrieval-augmented generation (RAG), it provides personalized, weather-based packing recommendations for US destinations.

## ✨ Features

- **🤖 Intelligent Agent System**: Zero-shot agent with dynamic tool selection
- **🌤️ Real-Time Weather Data**: Integration with the National Weather Service API
- **📚 Expert Knowledge Base**: RAG system with comprehensive wardrobe and packing guidelines
- **🔄 Sequential Chain Architecture**: Tools → Weather → Knowledge → Recommendations
- **💬 Natural Language Interface**: Simple conversational queries
- **🛡️ Robust Error Handling**: Graceful clarification loops for ambiguous requests

## 🏗️ Architecture

TempusVestis uses a "Tool-First" approach with three key components:

### 1. Deterministic Tools (Increment 1)

- **Date Operations**: Parse and calculate future dates
- **Weather API**: Retrieve weather forecasts for specific locations
- **Unit Tested**: Comprehensive test coverage for reliability

### 2. Agent Orchestration (Increment 2)

- **Zero-Shot Agent**: LangChain-powered agent with dynamic tool selection
- **Multi-Step Reasoning**: Automatically chains tool calls (date → weather → recommendation)
- **Error Handling**: Intelligent clarification when inputs are ambiguous

### 3. RAG Enhancement (Increment 3)

- **Vector Store**: FAISS-based knowledge base of wardrobe guidelines
- **Semantic Search**: Retrieves relevant packing advice based on conditions
- **Sequential Chain**: Combines real-time weather with expert knowledge

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/tempus-vestis.git
   cd tempus-vestis
   ```

2. **Install dependencies**

   ```bash
   pipenv install
   pipenv shell
   ```

3. **Set up environment variables**

   Create a `.env` file in the project root:

   ```text
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the application**

   ```bash
   python main.py
   ```

## 💡 Usage

### Interactive Mode

Simply run the application and describe your travel plans:

```bash
python main.py
```

Example queries:

- "What should I pack for Chicago in 7 days?"
- "I'm going to Miami next weekend, what should I wear?"
- "Help me pack for San Francisco 10 days from now"

### Single Query Mode

Pass a query as a command-line argument:

```bash
python main.py "What should I pack for New York in 5 days?"
```

### Jupyter Notebook (Development)

Explore the agent's reasoning in detail:

```bash
cd notebooks
jupyter notebook 02_agent_prototype.ipynb
```

## 🧪 Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src tests/
```

## 🔧 Technical Details

### Tools

1. **`get_current_date()`**: Returns the current date in ISO format
2. **`calculate_future_date(days: int)`**: Calculates a date N days in the future
3. **`get_weather_forecast(latitude: float, longitude: float)`**: Retrieves weather forecast from NWS API

### Agent Flow

```text
User Query → Agent Executor → Tool Selection → Weather Retrieval → RAG Chain → Final Recommendation
```

### RAG System

- **Embeddings**: OpenAI `text-embedding-3-small`
- **Vector Store**: FAISS for fast semantic search
- **Knowledge Base**: Comprehensive wardrobe guidelines covering:
  - Temperature-based recommendations
  - Weather condition strategies
  - Activity-specific advice
  - Packing optimization tips
  - Regional considerations

## 🌐 API Limitations

**Important**: The National Weather Service API only supports **US locations**. The agent will inform users if they request forecasts for international destinations.

## 📚 Development Plan

See [`docs/DEVELOPMENT_PLAN.md`](docs/DEVELOPMENT_PLAN.md) for the complete incremental development plan, including:

- ✅ Increment 0: Setup & Foundation
- ✅ Increment 1: The Code Tools
- ✅ Increment 2: The Agent's Brain
- ✅ Increment 3: Error & Multi-Step Flow

## 🤝 Contributing

This is a portfolio project demonstrating:

- LangChain agent orchestration
- Tool-first AI architecture
- RAG implementation
- Test-driven development
- Clean code structure

## 📄 License

This project is for portfolio and educational purposes.

## 🙏 Acknowledgments

- **LangChain**: For the excellent agent framework
- **National Weather Service**: For the free weather API
- **OpenAI**: For GPT-4 and embeddings models

## 📞 Contact

For questions or feedback, please reach out via GitHub issues.

---

## _Built with ❤️ using LangChain, OpenAI, and Python_
