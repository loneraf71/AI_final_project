Requirements for launching the website: 
 System Requirements
	1.  Python (>= 3.7) installed.
	2. 	Internet Connection for fetching results from external services such as:
	3. 	LLM (Ollama) for language model responses.
	4.  SerpAPI for Google search queries.
 
 Required Python Libraries
	1.	Streamlit (pip install streamlit) — for creating the web interface.
	2.	time (built-in Python library) — for adding delays and simulating progress bars.
	3.	PyPDF2 (pip install PyPDF2) — for extracting text from PDF documents.
	4.	sentence-transformers (pip install sentence-transformers) — for generating text embeddings.
	5.	chromadb (pip install chromadb) — for working with vector databases to store document embeddings.
	6.	os (built-in Python library) — for file path operations.
	7.	requests (pip install requests) — for making HTTP requests to external APIs (SerpAPI).
	8.	uuid (built-in Python library) — for generating unique document IDs.
	9.	langchain (pip install langchain) — for interacting with large language models.
 
 External Services & API Keys
	1.	Ollama (LLM Backend): Ensure that Ollama is installed and running on the user’s machine. This is required for generating AI responses.
	•	LLM Model: "llama3.2:latest" must be available in Ollama.
	•	Command to install Ollama: brew install ollama (if using macOS). Models must be downloaded separately.
	2.	SerpAPI API Key: A valid API key for SerpAPI is needed for Google search functionality.
	•	API_KEY = “437c9e22d88c1a62067b7e41fd39b00cf2c252308db785f284e8407008578079”`
	•	Users must sign up for a SerpAPI account and obtain their own API key if this one expires.
