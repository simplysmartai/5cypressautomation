import React, { useState, useEffect } from "react";

function SkillsDashboard() {
  const [skills, setSkills] = useState([]);
  const [activeSkill, setActiveSkill] = useState(null);
  const [formData, setFormData] = useState({});
  const [result, setResult] = useState(null);

  useEffect(() => {
    fetch("/api/skills")
      .then(res => res.json())
      .then(setSkills);
  }, []);

  const handleActivate = (skill) => {
    setActiveSkill(skill);
    setFormData({});
    setResult(null);
  };

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch(`/api/skills/${activeSkill.id}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData)
    });
    const data = await res.json();
    setResult(data);
  };

  return (
    <div>
      <h1>Skills Dashboard</h1>
      <ul>
        {skills.map(skill => (
          <li key={skill.id}>
            <strong>{skill.name}</strong> - {skill.description}
            <button onClick={() => handleActivate(skill)}>Activate</button>
          </li>
        ))}
      </ul>

      {activeSkill && (
        <div className="modal" style={{background: '#fff', border: '1px solid #ccc', padding: 20, position: 'fixed', top: 100, left: '50%', transform: 'translateX(-50%)', zIndex: 1000}}>
          <h2>{activeSkill.name}</h2>
          <form onSubmit={handleSubmit}>
            {activeSkill.inputs.map(input => (
              <div key={input.name}>
                <label>{input.label}</label>
                <input
                  type={input.type}
                  name={input.name}
                  value={formData[input.name] || ""}
                  onChange={handleInputChange}
                  required
                />
              </div>
            ))}
            <button type="submit">Run Skill</button>
            <button type="button" onClick={() => setActiveSkill(null)}>Cancel</button>
          </form>
          {result && (
            <div>
              <h3>Result:</h3>
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default SkillsDashboard;
