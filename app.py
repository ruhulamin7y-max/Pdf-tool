from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chalkboard Live Studio Pro</title>
    <link href="https://fonts.googleapis.com/css2?family=Gochi+Hand&family=Caveat:wght@700&family=Montserrat:wght@900&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/pptxgenjs@3.12.0/dist/pptxgen.bundle.js"></script>
    
    <style>
        :root {
            --board: #122b1e;
            --frame: #3d2b1f;
            --chalk: #fefefe;
            --accent: #ffd54f;
            --correct: #69f0ae;
            --blue: #81d4fa;
        }

        body { background: #0d1117; color: white; font-family: 'Montserrat', sans-serif; margin: 0; padding: 15px; }

        /* UI Styling */
        .container { max-width: 1100px; margin: 0 auto; }
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; justify-content: center; }
        .tab { padding: 12px 25px; background: #161b22; border: 1px solid #30363d; border-radius: 50px; cursor: pointer; font-weight: 800; color: #8b949e; transition: 0.3s; }
        .tab.active { background: var(--correct); color: #000; border-color: var(--correct); }

        textarea { width: 100%; height: 100px; background: #010409; color: var(--correct); border: 1px solid #30363d; border-radius: 8px; padding: 15px; font-size: 14px; margin-bottom: 15px; }
        
        .btn-row { display: flex; gap: 10px; margin-bottom: 30px; flex-wrap: wrap; }
        .btn { flex: 1; padding: 12px; border-radius: 8px; border: none; font-weight: 900; cursor: pointer; text-transform: uppercase; font-size: 12px; min-width: 140px; }
        .btn-green { background: #238636; color: white; }
        .btn-pdf { background: #455a64; color: white; }
        .btn-ppt { background: #bf360c; color: white; }

        /* REALISTIC CHALKBOARD DESIGN */
        .board-wrapper {
            border: 15px solid var(--frame);
            border-radius: 5px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.7);
            background: var(--board);
            aspect-ratio: 16/9;
            position: relative;
            margin-bottom: 40px;
            display: flex; flex-direction: column; justify-content: center;
            padding: 5% 8%;
            overflow: hidden;
            box-sizing: border-box;
        }

        /* Chalkboard Texture & White Dust/Noise */
        .board-wrapper::before {
            content: ""; position: absolute; inset: 0;
            background-image: 
                url('https://www.transparenttextures.com/patterns/black-board.png'),
                radial-gradient(circle at 20% 30%, rgba(255,255,255,0.05) 0%, transparent 40%),
                radial-gradient(circle at 80% 70%, rgba(255,255,255,0.03) 0%, transparent 30%);
            opacity: 0.7; pointer-events: none;
        }

        .q-text {
            font-family: 'Gochi Hand', cursive;
            font-size: clamp(22px, 4vw, 45px);
            color: var(--chalk);
            line-height: 1.3;
            margin-bottom: 30px;
            z-index: 2;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
        }

        .opt-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; z-index: 2; }
        .opt-item {
            font-family: 'Gochi Hand', cursive;
            font-size: clamp(18px, 2.5vw, 32px);
            color: var(--accent);
            padding: 10px;
            border-bottom: 1px dashed rgba(255,255,255,0.1);
            cursor: pointer;
        }
        .opt-item span { font-family: 'Montserrat'; margin-right: 10px; font-weight: 900; }

        /* Slide 2: Answer reveal */
        .ans-reveal { text-align: center; z-index: 2; width: 100%; }
        .ans-idx { font-size: clamp(80px, 12vw, 150px); font-weight: 900; color: var(--correct); margin: 0; text-shadow: 0 0 40px rgba(105,240,174,0.4); }
        .ans-text { font-size: clamp(24px, 4vw, 45px); color: white; font-family: 'Gochi Hand'; margin-bottom: 20px; }
        .exp-text { font-size: clamp(16px, 2vw, 26px); color: var(--blue); font-family: 'Gochi Hand'; max-width: 90%; margin: 0 auto; line-height: 1.4; }

        .hidden { display: none; }
        #status { text-align: center; color: var(--correct); font-weight: bold; margin-bottom: 10px; }

    </style>
</head>
<body>

<div class="container">
    <div class="tabs">
        <div class="tab active" onclick="showTab('input')">1. INPUT DATA</div>
        <div class="tab" onclick="showTab('preview')">2. PREVIEW SLIDES</div>
        <div class="tab" onclick="showTab('test')">3. LIVE TEST MODE</div>
    </div>

    <div id="tab-input" class="content-panel">
        <textarea id="mcqInput" placeholder="Paste: Question | Opt A | Opt B | Opt C | Opt D | Correct No (1-4) | Explanation"></textarea>
        <div class="btn-row">
            <button class="btn btn-green" onclick="generateData()">👁️ Generate Numbering</button>
            <button class="btn btn-pdf" onclick="exportPDF()">📄 Download Handwriting PDF</button>
            <button class="btn btn-ppt" onclick="exportPPT()">📊 Download Handwriting PPT</button>
        </div>
        <div id="status"></div>
    </div>

    <div id="tab-preview" class="content-panel hidden">
        <div id="preview-area"></div>
    </div>

    <div id="tab-test" class="content-panel hidden">
        <div id="test-area"></div>
        <div style="text-align: center; margin-top: 20px;">
            <button class="btn" style="background:#444; color:white; max-width:200px;" onclick="nextTest()">NEXT QUESTION →</button>
        </div>
    </div>
</div>

<script>
    let mcqData = [];
    let testIdx = 0;
    const LBL = ["A", "B", "C", "D"];

    function showTab(t) {
        document.querySelectorAll('.content-panel').forEach(p => p.classList.add('hidden'));
        document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
        document.getElementById('tab-' + t).classList.remove('hidden');
        event.currentTarget.classList.add('active');
        if(t === 'preview') renderPreview();
        if(t === 'test') startTest();
    }

    function generateData() {
        const text = document.getElementById('mcqInput').value.trim();
        mcqData = [];
        text.split('\\n').forEach(line => {
            if(!line.includes('|')) return;
            const c = line.split('|').map(s => s.trim()).filter(s => s !== '');
            if(c.length < 6 || c[0].toLowerCase().includes('question')) return;
            // Question numbering is handled by index automatically
            mcqData.push({ q: c[0], opts: [c[1], c[2], c[3], c[4]], ans: parseInt(c[5]) - 1, exp: c[6] || "" });
        });
        document.getElementById('status').innerText = `✅ Loaded ${mcqData.length} Questions with Auto-Numbering.`;
    }

    function renderPreview() {
        const area = document.getElementById('preview-area');
        area.innerHTML = '';
        mcqData.forEach((m, i) => {
            area.innerHTML += `
                <div class="board-wrapper">
                    <div class="q-text">Q. ${i + 1} ${m.q}</div>
                    <div class="opt-grid">
                        ${m.opts.map((o, oi) => `<div class="opt-item"><span>${LBL[oi]}</span> ${o}</div>`).join('')}
                    </div>
                </div>
                <div class="board-wrapper">
                    <div class="ans-reveal">
                        <div class="ans-idx">${LBL[m.ans]}</div>
                        <div class="ans-text">${m.opts[m.ans]}</div>
                        <div class="exp-text">Explanation: ${m.exp}</div>
                    </div>
                </div>
            `;
        });
    }

    // PDF Export: Using Font fallbacks for handwriting
    async function exportPDF() {
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF('l', 'mm', [297, 167]);
        mcqData.forEach((m, i) => {
            if(i > 0) pdf.addPage();
            // Slide 1: Q
            pdf.setFillColor(18, 43, 30); pdf.rect(0,0,297,167,'F');
            pdf.setTextColor(255,255,255); pdf.setFont("courier", "bolditalic"); pdf.setFontSize(30);
            pdf.text(pdf.splitTextToSize(`Q. ${i+1} ${m.q}`, 250), 20, 40);
            pdf.setTextColor(255, 213, 79); pdf.setFontSize(22);
            pdf.text(`A. ${m.opts[0]}`, 25, 100); pdf.text(`B. ${m.opts[1]}`, 150, 100);
            pdf.text(`C. ${m.opts[2]}`, 25, 130); pdf.text(`D. ${m.opts[3]}`, 150, 130);
            // Slide 2: Ans
            pdf.addPage();
            pdf.setFillColor(10, 30, 20); pdf.rect(0,0,297,167,'F');
            pdf.setTextColor(105, 240, 174); pdf.setFontSize(100); pdf.text(LBL[m.ans], 148, 70, {align:'center'});
            pdf.setTextColor(255,255,255); pdf.setFontSize(35); pdf.text(m.opts[m.ans], 148, 95, {align:'center'});
            pdf.setTextColor(129, 212, 250); pdf.setFontSize(16); pdf.text(pdf.splitTextToSize(m.exp, 240), 148, 120, {align:'center'});
        });
        pdf.save("Class_Handwriting_MCQ.pdf");
    }

    // PPT Export: Using System Handwriting Fonts
    async function exportPPT() {
        let pres = new PptxGenJS();
        pres.layout = 'LAYOUT_WIDE';
        mcqData.forEach((m, i) => {
            let s1 = pres.addSlide(); s1.background = { color: '122b1e' };
            s1.addText(`Q. ${i+1} ${m.q}`, { x:0.5, y:1, w:12, color:'FFFFFF', fontSize:34, fontFace:'Comic Sans MS', bold:true, align:'center' });
            s1.addText(`A. ${m.opts[0]}`, { x:1, y:4.2, w:5, color:'FFD54F', fontSize:26, fontFace:'Comic Sans MS' });
            s1.addText(`B. ${m.opts[1]}`, { x:7, y:4.2, w:5, color:'FFD54F', fontSize:26, fontFace:'Comic Sans MS' });
            s1.addText(`C. ${m.opts[2]}`, { x:1, y:5.8, w:5, color:'FFD54F', fontSize:26, fontFace:'Comic Sans MS' });
            s1.addText(`D. ${m.opts[3]}`, { x:7, y:5.8, w:5, color:'FFD54F', fontSize:26, fontFace:'Comic Sans MS' });

            let s2 = pres.addSlide(); s2.background = { color: '0A1E14' };
            s2.addText(LBL[m.ans], { x:0, y:1.5, w:13.3, color:'69F0AE', fontSize:120, align:'center', bold:true, fontFace:'Comic Sans MS' });
            s2.addText(m.opts[m.ans], { x:0, y:4.2, w:13.3, color:'FFFFFF', fontSize:45, align:'center', bold:true, fontFace:'Comic Sans MS' });
            s2.addText(m.exp, { x:1, y:5.8, w:11.3, color:'81D4FA', fontSize:22, align:'center', italic:true, fontFace:'Comic Sans MS' });
        });
        pres.writeFile({ fileName: 'YouTube_Class_MCQ.pptx' });
    }

    /* LIVE TEST LOGIC */
    function startTest() {
        testIdx = 0;
        renderTestSlide(false);
    }

    function renderTestSlide(revealed) {
        const area = document.getElementById('test-area');
        const m = mcqData[testIdx];
        if(!revealed) {
            area.innerHTML = `
                <div class="board-wrapper">
                    <div class="q-text">Q. ${testIdx + 1} ${m.q}</div>
                    <div class="opt-grid">
                        ${m.opts.map((o, oi) => `<div class="opt-item" onclick="renderTestSlide(true)"><span>${LBL[oi]}</span> ${o}</div>`).join('')}
                    </div>
                </div>`;
        } else {
            area.innerHTML = `
                <div class="board-wrapper">
                    <div class="ans-reveal">
                        <div class="ans-idx">${LBL[m.ans]}</div>
                        <div class="ans-text">${m.opts[m.ans]}</div>
                        <div class="exp-text">${m.exp}</div>
                    </div>
                </div>`;
        }
    }

    function nextTest() {
        if(testIdx < mcqData.length - 1) { testIdx++; renderTestSlide(false); }
        else { alert("Test Completed!"); showTab('input'); }
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
