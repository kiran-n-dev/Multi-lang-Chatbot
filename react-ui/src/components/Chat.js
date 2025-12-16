import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
// import { franc } from 'franc'; // Not using for now

const Chat = ({ history, onNewMessage }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);

  // const detectLanguage = (text) => {
  //   const lang = franc(text);
  //   // Map to ISO 639-1 codes
  //   const langMap = {
  //     'eng': 'en',
  //     'spa': 'es',
  //     'fra': 'fr',
  //     'deu': 'de',
  //     'ita': 'it',
  //     'por': 'pt',
  //     'rus': 'ru',
  //     'ara': 'ar',
  //     'hin': 'hi',
  //     'chi': 'zh',
  //     'jpn': 'ja',
  //     'kor': 'ko'
  //   };
  //   return langMap[lang] || 'en';
  // };

  const sendMessage = async () => {
    if (!query.trim()) return;
    setLoading(true);
    // const userLang = detectLanguage(query); // Temporarily disabled to match Streamlit behavior
    const userMessage = { role: 'user', content: query };
    const newHistory = [...history, userMessage];
    onNewMessage(newHistory);
    
    try {
      const response = await axios.post('/api/chat', {
        query
        // userLang // Not sending to match Streamlit (no translation)
      });
      console.log('LLM Response:', response.data.text); // Debug log
      const assistantMessage = { role: 'assistant', content: response.data.text };
      onNewMessage([...newHistory, assistantMessage]);
      setQuery('');
    } catch (error) {
      const errorMessage = { role: 'assistant', content: 'Error: ' + (error.response?.data?.detail || error.message) };
      onNewMessage([...newHistory, errorMessage]);
    }
    setLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !loading) {
      sendMessage();
    }
  };

  return (
    <div>
      <h2>Ask Questions</h2>
      <div className="chat-history">
        {history.map((msg, idx) => (
          <div key={idx} className={msg.role}>
            <strong>{msg.role === 'user' ? 'You' : 'Assistant'}:</strong>
            <div style={{ marginTop: '5px' }}>
              <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeRaw]}>{msg.content}</ReactMarkdown>
            </div>
          </div>
        ))}
      </div>
      <div className="chat-input">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your question in any language..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !query.trim()}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
};

export default Chat;