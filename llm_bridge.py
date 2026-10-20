import requests
import json

def format_data_for_llm(teeth_data, probs_data):
    """
    แปลงข้อมูลจาก AI (JSON) ให้เป็นข้อความสรุป (Text)
    """
    findings = []
    
    # เรียงลำดับซี่ฟัน
    sorted_teeth = sorted(teeth_data.keys(), key=lambda x: int(x) if str(x).isdigit() else 999)
    found_any = False
    
    for tooth_id in sorted_teeth:
        is_caries = teeth_data[tooth_id]
        if is_caries:
            conf = probs_data.get(str(tooth_id), 0.0)
            
            # แปลงความมั่นใจเป็น -> ความรุนแรง
            severity = "Low confidence / Suspected"
            if conf > 0.8:
                severity = "High confidence / Clear lesion"
            elif conf > 0.6:
                severity = "Moderate confidence"
            
            findings.append(f"- Tooth #{tooth_id}: Caries Detected ({severity}, Score: {conf:.2f})")
            found_any = True

    if not found_any:
        return "No caries detected."
    
    return "\n".join(findings)

def ask_ollama(formatted_text):
    """
    ส่งข้อความไปให้ Ollama เขียน Report
    """
    prompt = f"""
    You are a professional Dental Radiologist Assistant. Write a medical report based on these findings.
    
    RULES:
    1. Use professional medical terms.
    2. Format: "Radiographic Findings" followed by "Conclusion".
    3. Do NOT invent symptoms not listed below.
    
    INPUT DATA:
    {formatted_text}
    
    MEDICAL REPORT:
    """

    try:
        # ยิงไปที่ Local Server (Ollama)
        response = requests.post('http://localhost:11434/api/generate', json={
            "model": "llama3.2",   # ต้องตรงกับรุ่นที่โหลดมา (เช่น llama3.2 หรือ phi3)
            "prompt": prompt,
            "stream": False,
            "temperature": 0.2
        }, timeout=45)
        
        if response.status_code == 200:
            return response.json().get('response', "Error: AI returned empty text")
        else:
            return f"Error: Ollama Server returned status {response.status_code}"
            
    except Exception as e:
        return f"Connection Error: Is Ollama running? ({str(e)})"