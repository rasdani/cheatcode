import React, { useState } from 'react';
import axios from 'axios';
import './Chat.css';
import ReactMarkdown from 'react-markdown';

// hardcode the API endpoint for now
const REACT_APP_API_ENDPOINT = "http://localhost:8000";

function Chat() {
  // hooks to manage the state of the chat messages and the input message
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sourceDocs, setSourceDocs] = useState({});

  // handles submission of the user's message
  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent default page refresh on submit

    // add the user's message to the messages array
    setMessages([...messages, { type: 'user', text: inputMessage }]);

    // clear the input field
    setInputMessage('');

    // send a request to the backend with the user's message and handle the response
    try {
      const response = await axios.post(`${REACT_APP_API_ENDPOINT}/chat`, { question: inputMessage });

      // add the bot's response to the messages array
      setMessages([...messages, { type: 'user', text: inputMessage }, { type: 'bot', text: response.data.answer, id: messages.length + 1 }]);

      // save the source documents for the response
      setSourceDocs({ ...sourceDocs, [messages.length + 1]: response.data.source_documents });
    } catch (error) {
      console.error('Error fetching response from the backend:', error);
    }
  };

  // render messages with code snippets
  const renderMessage = (message) => {
    const codeBlockRegex = /```([\s\S]*?)```/g;
    const codeSnippets = message.text.match(codeBlockRegex) || [];
    const textWithoutCode = message.text.replace(codeBlockRegex, '').trim();

    // handle copying code snippets to clipboard
    const handleCopyClick = async (snippet) => {
      try {
        await navigator.clipboard.writeText(snippet.slice(3, -3));
      } catch (error) {
        console.error('Failed to copy code snippet:', error);
      }
    };

    return (
      <React.Fragment>
        {textWithoutCode && (
          <div className={`message ${message.type}`}>
            <ReactMarkdown>{textWithoutCode}</ReactMarkdown>
          </div>
        )}
        {codeSnippets.map((snippet, index) => (
          <React.Fragment key={index}>
            <pre className={`code-snippet ${message.type}`}>
              <code>{snippet.slice(3, -3)}</code>
            </pre>
            <button
              className={`copy-button ${message.type}`}
              onClick={() => handleCopyClick(snippet)}
            >
              Copy
            </button>
          </React.Fragment>
        ))}
      </React.Fragment>
    );
  };

  const toggleSourceDocs = (id) => {
    const message = messages.find(msg => msg.id === id);
    if (message.showSourceDocs) {
      message.showSourceDocs = false;
    } else {
      message.showSourceDocs = true;
    }
    setMessages([...messages]);
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((message, index) => (
          <React.Fragment key={index}>
            {renderMessage(message)}
            {message.type === 'bot' && (
              <button
                className={`source-docs-toggle ${message.type}`}
                onClick={() => toggleSourceDocs(message.id)}
              >
                Toggle Source Documents
              </button>
            )}
            {message.showSourceDocs && (
              <div className={`source-docs ${message.type}`}>
                {sourceDocs[message.id].map((doc, i) => (
                  <React.Fragment key={i}>
                <div className="source-docs-filepath"><strong>{doc.metadata.source}</strong></div>
                        <ReactMarkdown>{`\`\`\`${doc.page_content}\`\`\``}</ReactMarkdown>
                        <hr />
                      </React.Fragment>
                ))}
              </div>
            )}
          </React.Fragment>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          className="chat-input"
          placeholder="Type your message..."
        />
        <button type="submit" className="chat-submit-button">Send</button>
      </form>
    </div>
  );
}

export default Chat;