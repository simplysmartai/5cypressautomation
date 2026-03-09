/**
 * routes/api-skills.js
 * Skills dashboard API — list skills and run execution scripts.
 */
const express    = require('express');
const path       = require('path');
const fs         = require('fs');
const { exec }   = require('child_process');
const adminAuth  = require('../middleware/adminAuth');

const router = express.Router();
const ROOT      = path.join(__dirname, '..');
const skillsPath = path.join(ROOT, 'skills', 'skills.json');

router.get('/', (_req, res) => {
  if (!fs.existsSync(skillsPath)) {
    return res.status(404).json({ error: 'Skills config not found' });
  }
  res.json(JSON.parse(fs.readFileSync(skillsPath, 'utf8')));
});

router.post('/:id/run', adminAuth, (req, res) => {
  if (!fs.existsSync(skillsPath)) {
    return res.status(404).json({ error: 'Skills config not found' });
  }
  const skills = JSON.parse(fs.readFileSync(skillsPath, 'utf8'));
  const skill  = skills.find(s => s.id === req.params.id);
  if (!skill) return res.status(404).json({ error: 'Skill not found' });

  let cmd = `python execution/${skill.id}.py`;
  for (const input of (skill.inputs || [])) {
    const val = req.body[input.name] || '';
    if (val) cmd += ` --${input.name} "${val.replace(/"/g, '\\"')}"`;
  }

  console.log(`[SKILL RUN] ${skill.name}: ${cmd}`);

  exec(cmd, { timeout: 60_000 }, (err, stdout, stderr) => {
    if (err) {
      console.error(`[SKILL ERROR] ${skill.name}:`, stderr);
      return res.status(500).json({
        error: stderr || err.message,
        skill: skill.name,
        tip: 'Check that the execution script exists and dependencies are installed.'
      });
    }
    console.log(`[SKILL OK] ${skill.name}`);
    res.json({ output: stdout, skill: skill.name });
  });
});

module.exports = router;
