# LaborLawAgent

Consultation agent for Labor Law and Payroll Processing in Portugal. This system was developed to provide accurate answers based exclusively on official sources (ACT, DRE, and Portal das Finanças), utilizing real-time search mechanisms to avoid obsolete data.

## Configuration and Execution

To run the agent locally, follow the steps below:

1. Create and activate the virtual environment:
python -m venv venv
.\venv\Scripts\activate

2. Install the necessary libraries:
pip install openai pytest python-dotenv

3. Configure the API key:
Create a .env file in the root of the project with the following content:
OPENAI_API_KEY=your_key_here

Or define it directly in the terminal:
$env:OPENAI_API_KEY="your_key_here"

4. Quick execution:
Open the python interpreter and execute:
from agent import LaborLawAgent
agente = LaborLawAgent()
print(agente.chat("What is the minimum wage in 2024?"))

## Project Structure and Technical Decisions

The agent was built on a Tool Calling architecture. The decision for this model is due to the volatile nature of IRS withholding tables and legislative updates in Portugal. Instead of relying on the LLM's pre-trained knowledge, the system works as an orchestrator that searches the web, extracts relevant information from government domains, and synthesizes the response with the proper citation.

Key implementation points:
- Grounding: All technical answers are obligatorily accompanied by the URL of the official source.
- Security: Implementation of scope filters to prevent the agent from answering topics outside of Labor Law or providing illegal advice.
- Modularity: The LaborLawAgent class was designed to be easily integrated into other systems or interfaces.

## Automated Tests

A test suite was included to validate the reliability of the system:

To run the accuracy and citation tests:
pytest test_eval.py

The tests verify:
- Presence of exact values (e.g., TSU rates, notice periods).
- Mandatory citations from .gov.pt domains.
- The agent's behavior towards out-of-scope questions.

## Technical Report

The architectural decisions, evaluation results (V1 vs. V2), and future development steps are detailed in the **`Technical_Report_HomoDeus.pdf`** file, included in the root of this repository.

---
Project developed for the HomoDeusAI technical challenge.
