import gradio as gr
import google.generativeai as genai
from fpdf import FPDF
from datetime import datetime
import os

# === Gemini API Config ===
genai.configure(api_key="AIzaSyABjjtDkWlJTGYgy5mkagHlDAEhpPTm1JI")
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

feedback_history = []

# === Feedback Generator ===
def generate_feedback(text, depth):
    prompt = (
        f"You are an AI reviewer. Analyze this project brief with {depth.lower()} depth.\n"
        f"Provide a structured response with:\n"
        f"- Summary\n- Strengths\n- Weaknesses\n- Suggestions\n"
        f"- Clarity score (1–10)\n- Innovation score (1–10)\n\nBRIEF:\n{text}"
    )
    try:
        response = model.generate_content(prompt)
        feedback = response.text.strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        feedback_history.append(f"[{timestamp}] {depth} review")
        return feedback, "\n".join(feedback_history[-5:])
    except Exception as e:
        return f"Error: {str(e)}", "\n".join(feedback_history[-5:])

# === PDF Export ===
def save_as_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    filename = f"AI_Feedback_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

# === File Reader ===
def read_file(file):
    if file is None:
        return ""
    ext = os.path.splitext(file.name)[-1]
    if ext == ".txt":
        return open(file.name, "r", encoding="utf-8").read()
    elif ext == ".pdf":
        import fitz  # PyMuPDF
        doc = fitz.open(file.name)
        return "\n".join([page.get_text() for page in doc])
    return "Unsupported file type."

# === App UI ===
with gr.Blocks(css="""
    .gr-block.gr-box {
        max-width: 900px;
        margin: auto;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 30px 40px;
        box-shadow: 0 0 8px rgba(0,0,0,0.05);
        background-color: #ffffff;
    }
    .gr-button {
        font-weight: bold;
        padding: 12px 16px;
        border-radius: 8px;
    }
    .main-title {
        text-align: center;
        font-size: 2rem;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #666;
        margin-bottom: 30px;
        font-size: 1rem;
    }
    footer {
        text-align: center;
        font-size: 0.9rem;
        color: #aaa;
        margin-top: 40px;
    }
""") as app:
    
    gr.HTML("<h1 class='main-title'>AI Project Feedback Generator</h1>")
    gr.HTML("<p class='sub-title'>Paste or upload your project brief and get structured feedback including strengths, weaknesses, and ratings.</p>")

    with gr.Row():
        with gr.Column():
            brief_input = gr.Textbox(label="Paste Your Project Brief", lines=10, placeholder="Describe the project or upload a file instead")
            upload_file = gr.File(label="Upload .txt or .pdf", file_types=[".txt", ".pdf"])
            load_btn = gr.Button("📄 Load File")

            depth = gr.Radio(["Basic", "Detailed", "Expert"], label="Select Feedback Depth", value="Detailed")
            generate_btn = gr.Button("✨ Generate AI Feedback")

        with gr.Column():
            output_box = gr.Textbox(label="AI-Generated Feedback", lines=20, interactive=False)
            history_box = gr.Textbox(label="Feedback History", lines=6, interactive=False)
            pdf_btn = gr.Button("📥 Download as PDF")
            file_output = gr.File(label="Download Link")

    # Functions
    generate_btn.click(fn=generate_feedback, inputs=[brief_input, depth], outputs=[output_box, history_box])
    load_btn.click(fn=read_file, inputs=upload_file, outputs=brief_input)
    pdf_btn.click(fn=save_as_pdf, inputs=output_box, outputs=file_output)

    gr.HTML("<footer>© 2024 AI Project Feedback Tool · Built with Python, Gradio & Gemini</footer>")

app.launch()
