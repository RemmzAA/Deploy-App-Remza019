import React, { useState, useEffect } from 'react';
import './PollsWidget.css';

const PollsWidget = ({ user }) => {
  const [polls, setPolls] = useState([]);
  const [voted, setVoted] = useState({});

  useEffect(() => {
    fetchActivePolls();
    
    // Refresh every 10 seconds
    const interval = setInterval(fetchActivePolls, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchActivePolls = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/polls/active`);
      const data = await response.json();
      setPolls(data.polls || []);
    } catch (error) {
      console.error('Failed to fetch polls:', error);
    }
  };

  const vote = async (pollId, optionId) => {
    if (!user) {
      alert('Please login to vote!');
      return;
    }

    if (voted[pollId]) {
      alert('You have already voted in this poll!');
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/polls/vote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          poll_id: pollId,
          option_id: optionId,
          user_id: user.id.toString(),
          username: user.username
        }),
      });

      if (response.ok) {
        alert('✅ Vote recorded! +3 points earned!');
        setVoted({...voted, [pollId]: true});
        fetchActivePolls();
      } else {
        const error = await response.json();
        alert(`❌ ${error.detail}`);
      }
    } catch (error) {
      console.error('Vote error:', error);
      alert('❌ Failed to vote');
    }
  };

  if (polls.length === 0) {
    return null;
  }

  return (
    <div className="polls-widget">
      <h3 className="polls-title">🗳️ ACTIVE POLLS</h3>
      {polls.map(poll => (
        <div key={poll.id} className="poll-widget-card">
          <div className="poll-widget-header">
            <h4>{poll.question}</h4>
            <span className="poll-widget-votes">{poll.total_votes} votes</span>
          </div>
          
          <div className="poll-widget-options">
            {poll.options.map(option => {
              const percentage = poll.total_votes > 0 
                ? (option.votes / poll.total_votes * 100).toFixed(1)
                : 0;
              
              return (
                <button
                  key={option.id}
                  className={`poll-widget-option ${voted[poll.id] ? 'disabled' : ''}`}
                  onClick={() => vote(poll.id, option.id)}
                  disabled={voted[poll.id]}
                >
                  <div className="option-text">
                    <span>{option.text}</span>
                    <span className="option-percentage">{percentage}%</span>
                  </div>
                  <div 
                    className="option-bar"
                    style={{ width: `${percentage}%` }}
                  ></div>
                </button>
              );
            })}
          </div>
          
          <div className="poll-widget-footer">
            {!voted[poll.id] && user && (
              <span className="poll-reward">Vote to earn +3 points! 🎯</span>
            )}
            {voted[poll.id] && (
              <span className="poll-voted">✅ You voted!</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default PollsWidget;
