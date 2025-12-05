import React, { useState, useEffect } from 'react';
import './PredictionsWidget.css';

const PredictionsWidget = ({ user }) => {
  const [predictions, setPredictions] = useState([]);
  const [predicted, setPredicted] = useState({});

  useEffect(() => {
    fetchActivePredictions();
    
    // Refresh every 10 seconds
    const interval = setInterval(fetchActivePredictions, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchActivePredictions = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/predictions/active`);
      const data = await response.json();
      setPredictions(data.predictions || []);
    } catch (error) {
      console.error('Failed to fetch predictions:', error);
    }
  };

  const predict = async (predictionId, choice) => {
    if (!user) {
      alert('Please login to make predictions!');
      return;
    }

    if (predicted[predictionId]) {
      alert('You have already made a prediction!');
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/predictions/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prediction_id: predictionId,
          choice: choice,
          user_id: user.id.toString(),
          username: user.username
        }),
      });

      if (response.ok) {
        alert(`✅ Prediction recorded! +7 points earned!`);
        setPredicted({...predicted, [predictionId]: choice});
        fetchActivePredictions();
      } else {
        const error = await response.json();
        alert(`❌ ${error.detail}`);
      }
    } catch (error) {
      console.error('Prediction error:', error);
      alert('❌ Failed to make prediction');
    }
  };

  if (predictions.length === 0) {
    return null;
  }

  return (
    <div className="predictions-widget">
      <h3 className="predictions-title">🎯 ACTIVE PREDICTIONS</h3>
      {predictions.map(pred => (
        <div key={pred.id} className="prediction-widget-card">
          <div className="prediction-widget-header">
            <h4>{pred.question}</h4>
            <span className="prediction-widget-votes">{pred.total_votes} predictions</span>
          </div>
          
          <div className="prediction-widget-options">
            <button
              className={`prediction-option option-a ${predicted[pred.id] === 'a' ? 'selected' : ''}`}
              onClick={() => predict(pred.id, 'a')}
              disabled={predicted[pred.id]}
            >
              <div className="prediction-label">A</div>
              <div className="prediction-text">{pred.option_a}</div>
              {pred.result && (
                <div className="prediction-votes">{pred.votes_a} votes</div>
              )}
              {pred.result === 'a' && (
                <div className="winner-badge">🏆 WINNER</div>
              )}
            </button>
            
            <div className="vs-divider">VS</div>
            
            <button
              className={`prediction-option option-b ${predicted[pred.id] === 'b' ? 'selected' : ''}`}
              onClick={() => predict(pred.id, 'b')}
              disabled={predicted[pred.id]}
            >
              <div className="prediction-label">B</div>
              <div className="prediction-text">{pred.option_b}</div>
              {pred.result && (
                <div className="prediction-votes">{pred.votes_b} votes</div>
              )}
              {pred.result === 'b' && (
                <div className="winner-badge">🏆 WINNER</div>
              )}
            </button>
          </div>
          
          <div className="prediction-widget-footer">
            {!predicted[pred.id] && !pred.result && user && (
              <span className="prediction-reward">Predict to earn +7 points! 🎯</span>
            )}
            {predicted[pred.id] && !pred.result && (
              <span className="prediction-waiting">⏳ Waiting for result...</span>
            )}
            {pred.result && (
              <span className="prediction-resolved">
                ✅ Resolved! Option {pred.result.toUpperCase()} won!
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default PredictionsWidget;
