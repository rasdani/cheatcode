import React, { useState } from 'react';
import axios from 'axios';

const REACT_APP_API_ENDPOINT="http://localhost:8000";

function Chat() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    // const response = await axios.post('http://localhost:8000/chat', { question });
    console.log('{ question }:', { question });
    const response = await axios.post(`${REACT_APP_API_ENDPOINT}/chat`, { question });
      
    setAnswer(response.data.answer);
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input type="text" value={question} onChange={(e) => setQuestion(e.target.value)} />
        <button type="submit">Ask</button>
      </form>
      {answer && <p>{answer}</p>}
    </div>
  );
}

export default Chat;
