"""
Builds a self-contained static docs/index.html for GitHub Pages deployment.
Embeds all band data as JSON and replaces HTMX with vanilla JS filtering/sorting.
"""

import csv
import json
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
data_path = project_root / "data" / "mdf_bands.csv"
output_path = project_root / "docs" / "index.html"


def load_bands():
    with open(data_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build():
    bands = load_bands()
    bands_json = json.dumps(bands, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MDF 2026</title>
    <style>
        :root, .theme-death {{
            --bg: #000000;
            --bg-secondary: #0d0d0d;
            --text: #b8b8b8;
            --text-bright: #e8e8e8;
            --accent: #ff0000;
            --border: #333;
            --rating-glow: none;
        }}

        .theme-black {{
            --bg: #050810;
            --bg-secondary: #0a0f18;
            --text: #6080a0;
            --text-bright: #c0d8f0;
            --accent: #40d0ff;
            --border: #1a2a40;
            --rating-gold: #ffd700;
        }}

        :root {{ color-scheme: dark; }}

        * {{ box-sizing: border-box; }}

        body {{
            font-family: 'Courier New', monospace;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 2rem;
            min-height: 100vh;
            border: 8px solid var(--border);
        }}

        h1 {{
            color: var(--accent);
            font-weight: bold;
            margin-bottom: 1.5rem;
            letter-spacing: 0.3em;
            text-transform: uppercase;
            font-size: 2.5rem;
            border-bottom: 4px solid var(--accent);
            padding-bottom: 0.5rem;
        }}

        .controls {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
            align-items: center;
        }}

        .filters {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            flex: 1;
        }}

        .clear-btn {{
            background: var(--accent);
            color: var(--bg);
            border: 2px solid var(--accent);
            padding: 0.5rem 1.5rem;
            font-family: inherit;
            font-weight: bold;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            cursor: pointer;
            transition: all 0.1s;
            text-decoration: none;
        }}

        .clear-btn:hover {{
            background: var(--bg);
            color: var(--accent);
        }}

        input, select {{
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            color: var(--text-bright);
            padding: 0.75rem 1rem;
            font-family: inherit;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            transition: all 0.2s;
        }}

        input:focus, select:focus {{
            outline: none;
            border-color: var(--accent);
        }}

        input::placeholder {{
            color: var(--text);
            text-transform: uppercase;
        }}

        .key {{
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            padding: 1rem;
            margin-bottom: 2rem;
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }}

        .key span {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .key .symbol {{
            color: var(--accent);
            font-size: 1.1rem;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            border: 2px solid var(--border);
        }}

        th {{
            text-align: left;
            background: var(--bg-secondary);
            border-bottom: 4px solid var(--accent);
            padding: 1rem 0.75rem;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            font-size: 0.75rem;
        }}

        th button.sort-link {{
            background: none;
            border: none;
            color: var(--text-bright);
            font-family: inherit;
            font-weight: bold;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.15em;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0;
            transition: color 0.1s;
        }}

        th button.sort-link:hover {{
            color: var(--accent);
        }}

        td {{
            padding: 0.75rem;
            border-bottom: 1px solid var(--border);
            font-size: 0.85rem;
        }}

        tr:hover td {{
            background: var(--bg-secondary);
            color: var(--text-bright);
        }}

        tr.must-see td {{
            background: rgba(255, 0, 0, 0.15);
            border-left: 3px solid var(--accent);
        }}

        .theme-black tr.must-see td {{
            background: rgba(64, 208, 255, 0.1);
        }}

        tr.must-see td:first-child {{
            color: var(--accent);
        }}

        tr.must-see:hover td {{
            background: rgba(255, 0, 0, 0.25);
        }}

        .theme-black tr.must-see:hover td {{
            background: rgba(64, 208, 255, 0.2);
        }}

        tr td:first-child {{
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .rating {{
            color: var(--accent);
            letter-spacing: 0.3em;
            font-size: 1rem;
        }}

        td.link {{ text-align: center; }}

        td.link a {{
            color: var(--accent);
            display: inline-block;
        }}

        td.link a:hover {{ transform: scale(1.2); }}

        td.notes {{
            color: var(--text);
            font-style: italic;
            max-width: 200px;
        }}

        .empty {{
            color: var(--text);
            text-align: center;
            padding: 3rem;
            text-transform: uppercase;
            letter-spacing: 0.2em;
        }}

        .fade-in {{
            animation: fadeIn 0.2s ease-out;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}

        .theme-toggle {{
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            color: var(--text-bright);
            padding: 0.5rem 1rem;
            font-family: inherit;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .theme-toggle:hover {{
            border-color: var(--accent);
            color: var(--accent);
        }}

        .header-row {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
        }}

        .header-row h1 {{
            margin-bottom: 0;
            flex: 1;
        }}

        .theme-toggle-wrapper {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        @media (max-width: 768px) {{
            body {{ padding: 1rem; border-width: 4px; }}
            h1 {{ font-size: 1.5rem; letter-spacing: 0.2em; }}
            .header-row {{ flex-direction: column; }}
            .header-row h1 {{ width: 100%; }}
            .theme-toggle-wrapper {{ width: 100%; }}
            .theme-toggle {{ width: 100%; }}
            .controls {{ flex-direction: column; }}
            .filters {{ width: 100%; }}
            .filters input, .filters select {{ width: 100%; }}
            .clear-btn {{ width: 100%; text-align: center; }}
            .key {{ flex-direction: column; gap: 0.5rem; }}
            table {{ display: none; }}
            .cards {{ display: flex; flex-direction: column; gap: 1rem; }}
            .card {{
                display: flex;
                flex-direction: column;
                background: var(--bg-secondary);
                border: 2px solid var(--border);
                padding: 1rem;
            }}
            .card.must-see {{ border-left: 3px solid var(--accent); }}
            .card-header {{
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 0.5rem;
                margin-bottom: 0.5rem;
            }}
            .card-band {{
                font-size: 1.1rem;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: var(--text-bright);
            }}
            .card.must-see .card-band {{ color: var(--accent); }}
            .card-rating {{ font-size: 1.2rem; color: var(--accent); letter-spacing: 0.2em; }}
            .card-meta {{ font-size: 0.8rem; color: var(--text); margin-bottom: 0.5rem; }}
            .card-genre {{ font-size: 0.75rem; color: var(--text); font-style: italic; margin-bottom: 0.5rem; }}
            .card-notes {{
                font-size: 0.8rem;
                color: var(--text);
                font-style: italic;
                border-top: 1px solid var(--border);
                padding-top: 0.5rem;
                margin-top: 0.5rem;
            }}
            .card-footer {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 0.5rem;
            }}
            .card-link a {{ color: var(--accent); }}
        }}

        @media (min-width: 769px) {{
            .cards {{ display: none; }}
            .card {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="header-row">
        <h1>☠ MDF 2026</h1>
        <div class="theme-toggle-wrapper">
            <select id="theme-toggle" class="theme-toggle">
                <option value="death">☠ Death</option>
                <option value="black">❄ Black</option>
            </select>
        </div>
    </div>

    <div class="controls">
        <div class="filters" id="filter-form">
            <input type="text" id="q" placeholder="Search...">
            <select id="day-select">
                <option value="">All Days</option>
                <option value="Wednesday">Wednesday (Pre-Fest)</option>
                <option value="Thursday">Thursday</option>
                <option value="Friday">Friday</option>
                <option value="Saturday">Saturday</option>
                <option value="Sunday">Sunday</option>
            </select>
            <select id="stage-select">
                <option value="">All Stages</option>
                <option value="Power Plant Live">Power Plant Live</option>
                <option value="Market Place">Market Place</option>
                <option value="Nevermore Hall">Nevermore Hall</option>
                <option value="Soundstage">Soundstage</option>
                <option value="Angels Rock Bar">Angels Rock Bar</option>
            </select>
            <select id="genre-select">
                <option value="">All Genres</option>
                <option value="death">Death</option>
                <option value="black">Black</option>
                <option value="doom">Doom</option>
                <option value="thrash">Thrash</option>
            </select>
        </div>
        <button class="clear-btn" id="reset-btn">Reset</button>
    </div>

    <div class="key">
        <span><span class="symbol">⛧⛧</span> Must See</span>
        <span><span class="symbol">⛧</span> Recommended</span>
        <span><span class="symbol">✧</span> Worth Seeing</span>
        <span><span class="symbol">·</span> Skip</span>
    </div>

    <div id="table-container" class="fade-in">
        <table>
            <thead>
                <tr>
                    <th><button class="sort-link" data-col="band">Band</button></th>
                    <th><button class="sort-link" data-col="day">Day</button></th>
                    <th><button class="sort-link" data-col="stage">Stage</button></th>
                    <th><button class="sort-link" data-col="time">Time</button></th>
                    <th><button class="sort-link" data-col="genre">Genre</button></th>
                    <th><button class="sort-link" data-col="location">Location</button></th>
                    <th><button class="sort-link" data-col="must_see">Rating</button></th>
                    <th>MA</th>
                    <th>Notes</th>
                </tr>
            </thead>
            <tbody id="results"></tbody>
        </table>
        <div class="cards" id="cards"></div>
    </div>

    <script>
        const BANDS = {bands_json};

        let sortCol = 'day';
        let sortOrder = 'asc';

        function norm(s) {{
            return (s || '').toLowerCase().replace(/[^a-z0-9]/g, '');
        }}

        function rating(v) {{
            if (v === '0') return '⛧⛧';
            if (v === '1') return '⛧';
            if (v === '2') return '✧';
            return '·';
        }}

        function esc(s) {{
            return (s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
        }}

        function maIcon() {{
            return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>`;
        }}

        function filterAndSort() {{
            const q = document.getElementById('q').value.trim();
            const day = document.getElementById('day-select').value;
            const stage = document.getElementById('stage-select').value;
            const genre = document.getElementById('genre-select').value;

            let results = BANDS.filter(b => {{
                if (day && !norm(b.day).includes(norm(day))) return false;
                if (stage && !norm(b.stage).includes(norm(stage))) return false;
                if (genre && !norm(b.genre).includes(norm(genre))) return false;
                if (q) {{
                    const searchable = norm([b.band, b.genre, b.notes, b.location, b.stage, b.day].join(' '));
                    for (const term of q.split(/[ \t]+/)) {{
                        if (term && !searchable.includes(norm(term))) return false;
                    }}
                }}
                return true;
            }});

            results.sort((a, b) => {{
                let va, vb;
                if (sortCol === 'must_see') {{
                    va = parseInt(a.must_see) || 99;
                    vb = parseInt(b.must_see) || 99;
                    return sortOrder === 'asc' ? va - vb : vb - va;
                }}
                va = (a[sortCol] || '').toLowerCase();
                vb = (b[sortCol] || '').toLowerCase();
                if (va < vb) return sortOrder === 'asc' ? -1 : 1;
                if (va > vb) return sortOrder === 'asc' ? 1 : -1;
                return 0;
            }});

            return results;
        }}

        function render() {{
            const bands = filterAndSort();

            // Update sort button indicators
            document.querySelectorAll('.sort-link').forEach(btn => {{
                const col = btn.dataset.col;
                const base = btn.dataset.label || btn.textContent.replace(/ [▲▼]$/, '');
                btn.dataset.label = base;
                if (col === sortCol) {{
                    btn.textContent = base + ' ' + (sortOrder === 'asc' ? '▲' : '▼');
                }} else {{
                    btn.textContent = base;
                }}
            }});

            // Table rows
            const tbody = document.getElementById('results');
            if (bands.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="9" class="empty">No bands found</td></tr>';
            }} else {{
                tbody.innerHTML = bands.map(b => `
                    <tr class="band-row${{b.must_see === '0' ? ' must-see' : ''}}">
                        <td>${{esc(b.band)}}</td>
                        <td>${{esc(b.day)}}</td>
                        <td>${{esc(b.stage)}}</td>
                        <td>${{esc(b.time)}}</td>
                        <td>${{esc(b.genre)}}</td>
                        <td>${{esc(b.location)}}</td>
                        <td class="rating">${{rating(b.must_see)}}</td>
                        <td class="link">${{b.metal_archives ? `<a href="${{esc(b.metal_archives)}}" target="_blank" rel="noopener">${{maIcon()}}</a>` : ''}}</td>
                        <td class="notes">${{esc(b.notes)}}</td>
                    </tr>
                `).join('');
            }}

            // Mobile cards
            const cards = document.getElementById('cards');
            if (bands.length === 0) {{
                cards.innerHTML = '<div class="card"><div class="card-notes">No bands found</div></div>';
            }} else {{
                cards.innerHTML = bands.map(b => `
                    <div class="card${{b.must_see === '0' ? ' must-see' : ''}}">
                        <div class="card-header">
                            <span class="card-band">${{esc(b.band)}}</span>
                            <span class="card-rating">${{rating(b.must_see)}}</span>
                        </div>
                        <div class="card-meta">${{esc(b.day)}} · ${{esc(b.stage)}}${{b.time ? ' · ' + esc(b.time) : ''}}</div>
                        <div class="card-genre">${{esc(b.genre)}}</div>
                        ${{b.notes ? `<div class="card-notes">${{esc(b.notes)}}</div>` : ''}}
                        <div class="card-footer">
                            <span class="card-location">${{esc(b.location)}}</span>
                            <span class="card-link">${{b.metal_archives ? `<a href="${{esc(b.metal_archives)}}" target="_blank" rel="noopener">MA</a>` : ''}}</span>
                        </div>
                    </div>
                `).join('');
            }}
        }}

        // Sort header clicks
        document.querySelectorAll('.sort-link').forEach(btn => {{
            btn.addEventListener('click', () => {{
                const col = btn.dataset.col;
                if (sortCol === col) {{
                    sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
                }} else {{
                    sortCol = col;
                    sortOrder = 'asc';
                }}
                render();
            }});
        }});

        // Filter inputs
        let debounce;
        document.getElementById('q').addEventListener('input', () => {{
            clearTimeout(debounce);
            debounce = setTimeout(render, 300);
        }});
        ['day-select', 'stage-select', 'genre-select'].forEach(id => {{
            document.getElementById(id).addEventListener('change', render);
        }});

        // Reset
        document.getElementById('reset-btn').addEventListener('click', () => {{
            document.getElementById('q').value = '';
            document.getElementById('day-select').value = '';
            document.getElementById('stage-select').value = '';
            document.getElementById('genre-select').value = '';
            sortCol = 'day';
            sortOrder = 'asc';
            render();
        }});

        // Theme
        function applyTheme(theme) {{
            document.body.classList.remove('theme-death', 'theme-black');
            document.body.classList.add('theme-' + theme);
            localStorage.setItem('mdf-theme', theme);
        }}

        document.addEventListener('DOMContentLoaded', () => {{
            const saved = localStorage.getItem('mdf-theme') || 'death';
            applyTheme(saved);
            document.getElementById('theme-toggle').value = saved;
            document.getElementById('theme-toggle').addEventListener('change', function() {{
                applyTheme(this.value);
            }});
            render();
        }});
    </script>
</body>
</html>"""

    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"Built {output_path} ({len(bands)} bands)")


if __name__ == "__main__":
    build()
