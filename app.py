from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Realistic Chalkboard Studio</title>
    <!-- Premium Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Gochi+Hand&family=Patrick+Hand&family=Montserrat:wght@900&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/pptxgenjs@3.12.0/dist/pptxgen.bundle.js"></script>
    
    <style>
        :root {
            --board: #163022;
            --dust: rgba(255, 255, 255, 0.1);
            --frame: #3d2b1f;
            --accent: #ffd54f;
            --mint: #a5d6a7;
        }

        body {
            background: #0d1117; /* GitHub Dark */
            color: #c9d1d9;
            font-family: 'Montserrat', sans-serif;
            margin: 0; padding: 20px;
        }

        /* GitHub Style Input Card */
        .editor-container {
            max-width: 1000px; margin: 0 auto 40px;
            background: #161b22; border: 1px solid #30363d;
            border-radius: 10px; padding: 20px;
        }

        textarea {
            width: 100%; height: 120px;
            background: #010409; color: var(--mint);
            border: 1px solid #30363d; border-radius: 6px;
            padding: 12px; font-family: monospace; resize: none;
        }

        .actions { display: flex; gap: 10px; margin-top: 15px; }
        .btn {
            flex: 1; padding: 12px; border-radius: 6px; border: none;
            font-weight: 900; cursor: pointer; text-transform: uppercase;
        }
        .btn-green { background: #238636; color: white; }
        .btn-red { background: #da3633; color: white; }

        /* REALISTIC CHALKBOARD */
        .chalkboard {
            width: 100%; max-width: 900px; margin: 0 auto 50px;
            aspect-ratio: 16/9;
            background: var(--board);
            border: 15px solid var(--frame);
            border-radius: 4px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5), inset 0 0 100px rgba(0,0,0,0.4);
            position: relative;
            display: flex; flex-direction: column; justify-content: center;
            padding: 40px; overflow: hidden;
            box-sizing: border-box;
        }

        /* Realistic Chalk Dust & Texture */
        .chalkboard::before {
            content: ""; position: absolute; inset: 0;
            background-image: 
                url('https://www.transparenttextures.com/patterns/black-board.png'),
                radial-gradient(circle at 30% 30%, rgba(255,255,255,0.08) 0%, transparent 50%),
                radial-gradient(circle at 70% 60%, rgba(255,255,255,0.05) 0%, transparent 40%);
            opacity: 0.6; pointer-events: none;
        }

        /* Handwriting on Board */
        .q-text {
            font-family: 'Gochi Hand', cursive;
            font-size: 42px; line-height: 1.2;
            color: #fff; text-shadow: 2px 2px 3px rgba(0,0,0,0.3);
            margin-bottom: 25px; z-index: 2;
        }

        .options-grid {
            display: grid; grid-template-columns: 1fr 1fr; gap: 20px; z-index: 2;
        }

        .option {
            font-family: 'Patrick Hand', cursive;
            font-size: 32px; color: var(--accent);
            background: rgba(255,255,255,0.05);
            padding: 10px 20px; border-radius: 5px;
            border-bottom: 2px solid rgba(255,255,255,0.1);
        }

        /* Answer Reveal Style */
        .ans-reveal { text-align: center; z-index: 2; }
        .big-letter {
            font-size: 140px; font-weight: 900;
            color: var(--mint); margin: 0;
            text-shadow: 0 0 30px rgba(165,214,167,0.5);
        }
        .ans-desc { font-size: 40px; color: #fff; font-family: 'Gochi Hand'; }
        .exp { font-size: 26px; color: #81d4fa; font-family: 'Patrick Hand'; max-width: 80%; margin: 20px auto; }

        .chalk-holder {
            position: absolute; bottom: 5px; right: 20px;
            width: 60px; height: 10px; background: #eee;
            border-radius: 2px; opacity: 0.8;
        }

    </style>
</head>
<body>

<div class="container">
    <h1 style="text-align:center; font-family:'Caveat'; color:var(--accent); font-size:45px;">
        🖍️ YouTube Realistic Chalkboard
    </h1>

    <div class="editor-container">
        <textarea id="mcqInput" placeholder="Question | Option A | Option B | Option C | Option D | 1 | Explanation..."></textarea>
        <div class="actions">
            <button class="btn btn-green" onclick="process()">👁️ Preview Board</button>
            <button class="btn" style="background:#555; color:white;" onclick="exportPDF()">📄 Download PDF</button>
            <button class="btn btn-red" onclick="exportPPT()">📊 Download PPT</button>
        </div>
    </div>

    <div id="output"></div>
</div>

<script>
    let mcqData = [];
    const LBL = ["A", "B", "C", "D"];

    function process() {
        const text = document.getElementById('mcqInput').value.trim();
        mcqData = [];
        text.split('\\n').forEach(line => {
            const c = line.split('|').map(s=>s.trim());
            if(c.length >= 6) {
                mcqData.push({ q:c[0], opts:[c[1],c[2],c[3],c[4]], ans:parseInt(c[5])-1, exp:c[6]||"" });
            }
        });

        const out = document.getElementById('output');
        out.innerHTML = '';
        mcqData.forEach((m, i) => {
            out.innerHTML += `
                <!-- Slide 1 -->
                <div class="chalkboard">
                    <div class="q-text">${i+1}. ${m.q}</div>
                    <div class="options-grid">
                        ${m.opts.map((o,oi)=>`<div class="option"><b>${LBL[oi]}</b>. ${o}</div>`).join('')}
                    </div>
                    <div class="chalk-holder"></div>
                </div>
                <!-- Slide 2 -->
                <div class="chalkboard">
                    <div class="ans-reveal">
                        <div style="font-size:24px; color:var(--accent)">CORRECT ANSWER</div>
                        <div class="big-letter">${LBL[m.ans]}</div>
                        <div class="ans-desc">${m.opts[m.ans]}</div>
                        <div class="exp">Note: ${m.exp}</div>
                    </div>
                    <div class="chalk-holder"></div>
                </div>
            `;
        });
    }

    // PDF EXPORT FIX: 
    // PDF mein handwritten font lane ke liye hum "Times" ya "Courier" ko Bold Italic use karenge
    // realistic look ke liye background noise colors add karenge
    async function exportPDF() {
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF('l', 'mm', [297, 167]);
        
        mcqData.forEach((m, i) => {
            if(i>0) pdf.addPage();
            
            // Slide 1 Background
            pdf.setFillColor(22, 48, 34); pdf.rect(0, 0, 297, 167, 'F');
            // Dust effect (Fake noise)
            pdf.setDrawColor(255,255,255); pdf.setGState(new pdf.GState({opacity: 0.1}));
            for(let j=0; j<50; j++) pdf.circle(Math.random()*297, Math.random()*167, 0.5, 'F');
            pdf.setGState(new pdf.GState({opacity: 1.0}));

            pdf.setTextColor(255, 255, 255);
            pdf.setFont("courier", "bolditalic"); pdf.setFontSize(28);
            pdf.text(pdf.splitTextToSize(`${i+1}. ${m.q}`, 250), 20, 40);
            
            pdf.setTextColor(255, 213, 79); pdf.setFontSize(22);
            pdf.text(`A. ${m.opts[0]}`, 25, 90); pdf.text(`B. ${m.opts[1]}`, 150, 90);
            pdf.text(`C. ${m.opts[2]}`, 25, 120); pdf.text(`D. ${m.opts[3]}`, 150, 120);

            // Slide 2 Answer
            pdf.addPage();
            pdf.setFillColor(15, 30, 22); pdf.rect(0, 0, 297, 167, 'F');
            pdf.setTextColor(165, 214, 167); pdf.setFontSize(80);
            pdf.text(LBL[m.ans], 148, 65, {align:'center'});
            pdf.setTextColor(255, 255, 255); pdf.setFontSize(35);
            pdf.text(m.opts[m.ans], 148, 90, {align:'center'});
            pdf.setTextColor(129, 212, 250); pdf.setFontSize(16);
            pdf.text(pdf.splitTextToSize(m.exp, 220), 148, 120, {align:'center'});
        });
        pdf.save("Realistic_Chalkboard.pdf");
    }

    async function exportPPT() {
        let pres = new PptxGenJS();
        pres.layout = 'LAYOUT_WIDE';
        mcqData.forEach((m, i) => {
            let s1 = pres.addSlide();
            s1.background = { color: '163022' };
            s1.addText(`${i+1}. ${m.q}`, { x:0.5, y:1, w:12, color:'FFFFFF', fontSize:36, fontFace:'Comic Sans MS', bold:true, align:'center' });
            s1.addText(`A. ${m.opts[0]}`, { x:1, y:4, w:5, color:'FFD54F', fontSize:28, fontFace:'Comic Sans MS' });
            s1.addText(`B. ${m.opts[1]}`, { x:7, y:4, w:5, color:'FFD54F', fontSize:28, fontFace:'Comic Sans MS' });
            s1.addText(`C. ${m.opts[2]}`, { x:1, y:5.5, w:5, color:'FFD54F', fontSize:28, fontFace:'Comic Sans MS' });
            s1.addText(`D. ${m.opts[3]}`, { x:7, y:5.5, w:5, color:'FFD54F', fontSize:28, fontFace:'Comic Sans MS' });

            let s2 = pres.addSlide();
            s2.background = { color: '0d1f14' };
            s2.addText(LBL[m.ans], { x:0, y:1.5, w:13.3, color:'A5D6A7', fontSize:120, align:'center', bold:true });
            s2.addText(m.opts[m.ans], { x:0, y:4, w:13.3, color:'FFFFFF', fontSize:45, align:'center', bold:true });
            s2.addText(m.exp, { x:1, y:5.8, w:11.3, color:'81D4FA', fontSize:24, align:'center', italic:true });
        });
        pres.writeFile({ fileName: 'Realistic_Chalkboard.pptx' });
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
