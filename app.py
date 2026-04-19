from flask import Flask, render_template_string

app = Flask(__name__)

# The HTML/CSS/JS Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chalkboard Pro MCQ Studio</title>
    <!-- Professional Handwriting Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Gochi+Hand&family=Caveat:wght@700&family=Montserrat:wght@900&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/pptxgenjs@3.12.0/dist/pptxgen.bundle.js"></script>
    
    <style>
        :root {
            --board-bg: #123524; /* Deep Physiological Green */
            --frame: #3E2723;   /* Dark Walnut Wood */
            --chalk-white: #F8F8F8;
            --chalk-yellow: #FFD700;
            --chalk-mint: #98FB98;
            --chalk-blue: #87CEEB;
            --shadow: 0 10px 30px rgba(0,0,0,0.5);
        }

        body {
            background: #0d1117; /* GitHub Dark Theme Background */
            color: white;
            font-family: 'Montserrat', sans-serif;
            margin: 0;
            padding: 20px;
        }

        .container { max-width: 1100px; margin: 0 auto; }

        /* Input Area */
        .input-section {
            background: #161b22;
            padding: 25px;
            border-radius: 12px;
            border: 1px solid #30363d;
            margin-bottom: 30px;
        }

        textarea {
            width: 100%; height: 150px;
            background: #010409; color: var(--chalk-mint);
            border: 1px solid #30363d; border-radius: 8px;
            padding: 15px; font-family: monospace; font-size: 14px;
        }

        .btn-row { display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap; }
        .btn {
            flex: 1; padding: 15px; border-radius: 8px; border: none;
            cursor: pointer; font-weight: 900; text-transform: uppercase;
            font-size: 13px; transition: 0.2s;
        }
        .btn-preview { background: #238636; color: white; } /* GitHub Green */
        .btn-pdf { background: #30363d; color: white; border: 1px solid #8b949e; }
        .btn-ppt { background: #d1242f; color: white; }

        /* THE CHALKBOARD SLIDE - Optimized for 360p */
        .slide-frame {
            border: 18px solid var(--frame);
            border-radius: 10px;
            box-shadow: var(--shadow);
            background: var(--board-bg);
            aspect-ratio: 16/9;
            position: relative;
            margin-bottom: 50px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 40px 60px;
            overflow: hidden;
        }

        /* Chalkboard Texture */
        .slide-frame::before {
            content: ""; position: absolute; top:0; left:0; width: 100%; height:100%;
            background-image: url('https://www.transparenttextures.com/patterns/black-board.png');
            opacity: 0.15; pointer-events: none;
        }

        .q-text {
            font-family: 'Caveat', cursive;
            font-size: 48px; /* Large for low res */
            line-height: 1.2;
            color: var(--chalk-white);
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
            z-index: 2;
        }

        .options-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            z-index: 2;
        }

        .opt-box {
            font-family: 'Gochi Hand', cursive;
            font-size: 34px;
            color: var(--chalk-yellow);
            background: rgba(255,255,255,0.05);
            padding: 15px 25px;
            border-radius: 10px;
            border: 2px solid rgba(255,215,0,0.2);
        }

        .opt-box span {
            font-family: 'Montserrat', sans-serif;
            margin-right: 15px;
            font-weight: 900;
        }

        /* Slide 2: Answer Page */
        .answer-reveal { text-align: center; z-index: 2; }
        .ans-letter {
            font-size: 140px; /* Massive Visibility */
            font-weight: 900;
            color: var(--chalk-mint);
            margin: 0;
            text-shadow: 0 0 40px rgba(152,251,152,0.5);
        }
        .ans-text {
            font-size: 45px;
            color: white;
            margin-bottom: 25px;
            font-family: 'Gochi Hand', cursive;
        }
        .explanation {
            font-family: 'Gochi Hand', cursive;
            font-size: 30px;
            color: var(--chalk-blue);
            line-height: 1.4;
            max-width: 90%;
            margin: 0 auto;
        }

        #status-msg { text-align: center; color: var(--chalk-mint); margin-top: 10px; font-weight: bold; }
    </style>
</head>
<body>

<div class="container">
    <h2 style="text-align: center; font-family: 'Caveat'; font-size: 40px; color: var(--chalk-yellow);">
        🎓 YouTube Live MCQ Studio Pro
    </h2>

    <div class="input-section">
        <textarea id="mcqInput" placeholder="Format: Question | Option A | Option B | Option C | Option D | Correct No (1-4) | Explanation"></textarea>
        <div class="btn-row">
            <button class="btn btn-preview" onclick="renderPreview()">👁️ Preview Slides</button>
            <button class="btn btn-pdf" onclick="exportPDF()">📥 Download PDF</button>
            <button class="btn btn-ppt" onclick="exportPPT()">📊 Download PPT</button>
        </div>
        <div id="status-msg"></div>
    </div>

    <div id="preview-area">
        <!-- Slides will appear here -->
    </div>
</div>

<script>
    let mcqData = [];
    const LBL = ["A", "B", "C", "D"];

    function parseData() {
        const text = document.getElementById('mcqInput').value.trim();
        const data = [];
        text.split('\\n').forEach(line => {
            if (!line.includes('|')) return;
            const cols = line.split('|').map(c => c.trim()).filter(c => c !== '');
            if (cols.length < 6 || cols[0].toLowerCase().includes('question')) return;
            data.push({
                q: cols[0],
                opts: [cols[1], cols[2], cols[3], cols[4]],
                ans: parseInt(cols[5]) - 1,
                exp: cols[6] || ""
            });
        });
        return data;
    }

    function renderPreview() {
        mcqData = parseData();
        const area = document.getElementById('preview-area');
        area.innerHTML = '';
        
        mcqData.forEach((m, i) => {
            area.innerHTML += `
                <div style="text-align:center; margin-bottom:10px; color:#8b949e">--- Question ${i+1} ---</div>
                <!-- Slide 1 -->
                <div class="slide-frame">
                    <div class="q-text">${i+1}. ${m.q}</div>
                    <div class="options-grid">
                        ${m.opts.map((o, oi) => `<div class="opt-box"><span>${LBL[oi]}</span> ${o}</div>`).join('')}
                    </div>
                </div>
                <!-- Slide 2 -->
                <div class="slide-frame">
                    <div class="answer-reveal">
                        <div style="color:var(--chalk-yellow); font-size:24px;">CORRECT ANSWER</div>
                        <div class="ans-letter">${LBL[m.ans]}</div>
                        <div class="ans-text">${m.opts[m.ans]}</div>
                        <div class="explanation">📝 ${m.exp}</div>
                    </div>
                </div>
            `;
        });
    }

    async function exportPDF() {
        mcqData = parseData();
        if(!mcqData.length) return;
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF('l', 'mm', [297, 167]);

        mcqData.forEach((m, i) => {
            if (i > 0) pdf.addPage();
            // Q Page
            pdf.setFillColor(18, 53, 36); pdf.rect(0, 0, 297, 167, 'F');
            pdf.setTextColor(255, 255, 255); pdf.setFontSize(35);
            pdf.text(pdf.splitTextToSize(`${i+1}. ${m.q}`, 250), 20, 40);
            pdf.setTextColor(255, 215, 0); pdf.setFontSize(26);
            pdf.text(`A. ${m.opts[0]}`, 25, 100); pdf.text(`B. ${m.opts[1]}`, 150, 100);
            pdf.text(`C. ${m.opts[2]}`, 25, 130); pdf.text(`D. ${m.opts[3]}`, 150, 130);

            // Ans Page
            pdf.addPage();
            pdf.setFillColor(10, 30, 20); pdf.rect(0, 0, 297, 167, 'F');
            pdf.setTextColor(152, 251, 152); pdf.setFontSize(100); pdf.text(LBL[m.ans], 148, 70, {align:'center'});
            pdf.setTextColor(255, 255, 255); pdf.setFontSize(40); pdf.text(m.opts[m.ans], 148, 95, {align:'center'});
            pdf.setTextColor(135, 206, 235); pdf.setFontSize(20);
            pdf.text(pdf.splitTextToSize(m.exp, 240), 148, 120, {align:'center'});
        });
        pdf.save("Class_MCQ_Slides.pdf");
    }

    async function exportPPT() {
        mcqData = parseData();
        let pres = new PptxGenJS();
        pres.layout = 'LAYOUT_WIDE';

        mcqData.forEach((m, i) => {
            let s1 = pres.addSlide();
            s1.background = { color: '123524' };
            s1.addText(`${i+1}. ${m.q}`, { x:0.5, y:1.5, w:12, color:'FFFFFF', fontSize:40, bold:true, align:'center' });
            s1.addText(`A. ${m.opts[0]}`, { x:1, y:4.5, w:5, color:'FFD700', fontSize:30 });
            s1.addText(`B. ${m.opts[1]}`, { x:7, y:4.5, w:5, color:'FFD700', fontSize:30 });
            s1.addText(`C. ${m.opts[2]}`, { x:1, y:5.8, w:5, color:'FFD700', fontSize:30 });
            s1.addText(`D. ${m.opts[3]}`, { x:7, y:5.8, w:5, color:'FFD700', fontSize:30 });

            let s2 = pres.addSlide();
            s2.background = { color: '0A1E14' };
            s2.addText(LBL[m.ans], { x:0, y:1.5, w:13.3, color:'98FB98', fontSize:140, align:'center', bold:true });
            s2.addText(m.opts[m.ans], { x:0, y:4.2, w:13.3, color:'FFFFFF', fontSize:50, align:'center', bold:true });
            s2.addText(m.exp, { x:1, y:5.8, w:11.3, color:'87CEEB', fontSize:28, align:'center', italic:true });
        });
        pres.writeFile({ fileName: 'YouTube_Live_Class.pptx' }).then(() => {
            document.getElementById('status-msg').innerText = "✅ PPT READY!";
        });
    }
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True)
