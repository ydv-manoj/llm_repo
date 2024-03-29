# Environment variables
from dotenv import load_dotenv
load_dotenv()
# langchain_community for document loaders and vectorstores
from langchain_community.document_loaders.text import TextLoader
from langchain_community.vectorstores.faiss import FAISS

# langchain_text_splitters for splitting the text into chunks
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Incase of open source llms
from langchain.llms.huggingface_hub import HuggingFaceHub

# langchain_openai for chat_models and embeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

# langchain_core for prompt templates and messagesplaceholder - buffer memory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage

# langchain.chains
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

import os
#api_key=os.environ.get("API_KEY")

class TerraDX_GPT():
    # Intialize openai environment
    def __init__(self):
        
        # Maintain the chat history
        self.chat_history=[AIMessage(content="Hello there! I'm your assistant! Whether you're seeking information about Freeport McMoRan's operations, exploring annual reports or sustainaibility reports, I'm here to provide you with accurate and insightful answers. Let's dig into the fascinating world of geology and mining together!")]
        
        self.model=ChatOpenAI(temperature=0.2, model='gpt-4-turbo-preview',model_kwargs={"top_p":0.9, "presence_penalty":0.6}, max_tokens=1024)
        self.embeddings_model=OpenAIEmbeddings(model="text-embedding-3-large")
        # self.TerraDX_RAG()
        
    # Load the text files
    def document_loader(self,text_file):
        loader=TextLoader(text_file)
        loaded_text=loader.load()
        return loaded_text

    def get_text_chunks(self,text):
        text_splitter=RecursiveCharacterTextSplitter(
            # use default seperatros
            chunk_size=5000,
            chunk_overlap=1000,
            is_separator_regex=False
        )
        # Use split_documents if we have a text file containing all info
        chunks=text_splitter.split_documents(text)
        return chunks


    def get_all_document_chunks(self,root_dir):
        text_files=[]
        for root, dirs, files in os.walk(root_dir):
            if(len(files)>0):
                text_files.extend([os.path.join(root,file) for file in files])

        doc_chunks=[]
        for text_file in text_files:
            doc_chunks.extend(self.get_document_chunks(self.document_loader(text_file)))

        return doc_chunks
    
    # Create a vectorstore
    def get_vectorstore(self,text_chunks):
        #persistent_dir="/home/terradxllm/faiss_index"
        #if not os.path.exists(persistent_dir):
            #os.makedir()
        vectorstore=FAISS.from_documents(documents=text_chunks, embedding=self.embeddings_model)

        #vectorstore.save_local(persistent_dir)
        #new_db = FAISS.load_local(persistent_dir, self.embeddings_model)
        #docs = new_db.similarity_search(query)
        return vectorstore

    # Retrieval of context
    def get_context_retriever_chain(self,vectorstore):
        # Setting vectorstore as retriever
        context_retriever=vectorstore.as_retriever()

        # prompt engineering
        prompt=ChatPromptTemplate.from_messages(
            [MessagesPlaceholder(variable_name='chat_history'), ("user","{input}"),
            ("user","Given the above conversation, generate a search query to look up in order to get relevant information to the conversation")
        ])

        context_retriever_chain=create_history_aware_retriever(llm=self.model,retriever=context_retriever, prompt=prompt)
        return context_retriever_chain

    # Conversational chain using RAG
    def get_conversational_rag_chain(self,retriever_chain):
        prompt=ChatPromptTemplate.from_messages([
            ("system","""You will be provided with a context delimited by triple quotes. Your task is to analyse the context,Create a table to organize data or results if the problem involves multiple data points or comparisons and assist the user in providing factual answers. You must follow certain instructions given below:

            instructions:
            - Create a table to organize data or results if the problem involves multiple data points or comparisons. Ensure the table is sorted in ascending order.
            - Incase of mathematical questions, Identify the mathematical problem and define it clearly.
            - Break down the problem into smaller, manageable steps.
            - For each step, apply mathematical principles or calculations as required.
            - After completing the calculations, review each step and the final answer for accuracy.
            - Provide the final answer and confirm it by rechecking the calculations.
            - Use clear and concise language to explain the reasoning behind each step and the significance of the final answer.
            - give 2 line spacing between every point.
             
            example:
            "Calculate the total cost of 5 items priced at $3.50, $4.75, $2.00, $8.25, and $6.50, including a 5% sales tax."
            
            steps:
            - Creation Of Table and sorting in ascending or descending order
             table:
            - Item: Item 1, Price: $3.50
            - Item: Item 2, Price: $4.75
            - Item: Item 3, Price: $2.00
            - Item: Item 4, Price: $8.25
            - Item: Item 5, Price: $6.50
            
            Sorted: No
             
             table:
                - Item 3, Price: $2.00
                - Item 3, Price: $2.00
                - Item 1, Price: $3.50
                - Item 2, Price: $4.75
                - Item 5, Price: $6.50
                - Item 4, Price: $8.25
            
             sorted : Yes

            - Break down the problem: Calculate the sum of the item prices.
            - Calculate the sum: $3.50 + $4.75 + $2.00 + $8.25 + $6.50 = $25.00
            - Apply sales tax: $25.00 * 0.05 = $1.25
            - Calculate total cost: $25.00 + $1.25 = $26.25
            - Recheck calculations for accuracy.
            
            final_answer: "The total cost of the items, including sales tax, is $26.25."
            reasoning: "The total was calculated by summing the prices of all items and adding a 5% sales tax. The table was used to organize and ensure all item prices were accounted for and correctly added."

            notes:
            - Ensure accuracy by methodically following each step and rechecking the calculations.
            - The use of a table helps in visualizing and organizing data, making the calculation process clearer and more manageable.
            
            Answer the user's questions based on the below context: \n'''{context}''' """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user","{input}")])
        
        stuff_documents_chain=create_stuff_documents_chain(self.model, prompt)
        return create_retrieval_chain(retriever_chain, stuff_documents_chain)

    # Response retrieval
    def get_response(self,user_input):
        #vectorstore=get_vectorstore(get_all_text_chunks(root_dir))
        text_file_path="./10K2004.txt"
        vectorstore=self.get_vectorstore(self.get_text_chunks(self.document_loader(text_file_path)))
        context_retriever_chain=self.get_context_retriever_chain(vectorstore)
        conversation_rag_chain=self.get_conversational_rag_chain(context_retriever_chain)
        response=conversation_rag_chain.invoke({
            "chat_history": self.chat_history,
            "input": user_input
        })
        # print("\n\nFull response.............\n\n")
        # print(response)
        # print("\n\nAnswer only.............\n\n")
        # print(response["answer"])
        return response["answer"]

    # Input query and response
    def TerraDX_RAG(self):
        root_dir="./Text_Files"
        print(self.chat_history[0].content,"\n")
        # user input
        while True:
            user_query = input("Type your message here...!\n")
            if user_query.strip().lower()=="exit":
                break
            if user_query is not None and user_query != "":
                response = self.get_response(user_query)
                print(response)
                self.chat_history.append(HumanMessage(content=user_query))
                self.chat_history.append(AIMessage(content=response))
        
        new_query=input("\n\nDo you need more help?\n")
        if(new_query.lower()=="yes"):
            self.chat_history=[AIMessage(content="Hello there! I'm your assistant! Whether you're seeking information about Freeport McMoRan's operations, exploring annual reports or sustainaibility reports, I'm here to provide you with accurate and insightful answers. Let's dig into the fascinating world of geology and mining together!")]
            self.TerraDX_RAG()

# question="How much capital expenditure did freeport have in 2004?"
# question="Provide the 1 page summary of the given Freeport?"
# question="Provide the breakup of the total capital expenditure in 2004"
if __name__=="__main__":
    TerraDX_GPT_obj=TerraDX_GPT()
        
        
        
            
