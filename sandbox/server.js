const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

const GENERATED_SITES = '/app/generated_sites';

/**
 * POST /run
 * Execute and test generated site files
 * 
 * Request: { jobId: string, iteration: number, files: { filename: string }[] }
 * Response: { lighthouse_score: number, performance: number, seo: number, ... }
 */
app.post('/run', async (req, res) => {
  const { jobId, iteration, files } = req.body;

  try {
    // Create directory for this iteration
    const siteDir = path.join(GENERATED_SITES, jobId, `v${iteration}`);
    if (!fs.existsSync(siteDir)) {
      fs.mkdirSync(siteDir, { recursive: true });
    }

    // Write files to disk
    Object.entries(files).forEach(([filename, content]) => {
      fs.writeFileSync(path.join(siteDir, filename), content);
    });

    // Placeholder Lighthouse scores (Phase 5 will integrate real Lighthouse)
    const scores = {
      lighthouse_score: Math.floor(Math.random() * 30 + 70), // 70-100
      performance: Math.floor(Math.random() * 30 + 70),
      seo: Math.floor(Math.random() * 20 + 80),
      accessibility: Math.floor(Math.random() * 20 + 80),
      best_practices: Math.floor(Math.random() * 20 + 80),
      validation_errors: [],
    };

    res.json(scores);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

const PORT = 9000;
app.listen(PORT, () => {
  console.log(`✓ Sandbox server on port ${PORT}`);
});
