# from flask import Flask, render_template, request, jsonify, send_from_directory
# import os
# import cv2
# import numpy as np
# import base64
# import re
# import io
# import uuid
# import matplotlib.pyplot as plt
# from datetime import datetime
# from werkzeug.utils import secure_filename
# from dental_analysis_tool import DentalAnalyzer
# from evaluation import evaluate_caries_detection_fixed, generate_enhanced_report, visualize_enhanced_comparison

# # Import logging utilities
# import logging
# from logger_utils import setup_logger, log_image_processing, log_app_event, log_error

# ####################################################################################################
# ############################# ML Section ###########################################################
# ####################################################################################################

# # Initialize the analyzer with default or custom model paths
# analyzer = DentalAnalyzer(
#     tooth_detection_path='weights/Tooth_detect_pano_20250319.pt',
#     caries_segmentation_path='weights/Caries_seg_single_20250319.pth',
#     tooth_recognition_path='weights/Tooth_seg_pano_20250319.pt'
# )

# ## Process the Image function  ----------------------------------------
# def process_pipeline(pano_img, filename):
#     try:
#         log_image_processing(filename, "analyzer.analyze_image", "start")
#         results = analyzer.analyze_image(pano_img)
#         log_image_processing(filename, "analyzer.analyze_image", "complete")
#         return results['report'], results['caries_visualization']
#     except Exception as e:
#         log_error("process_pipeline", f"Failed to process image {filename}", e)
#         raise
    
# ####################################################################################################
# ############################# App Section ##########################################################
# ####################################################################################################

# # Initialize the Flask app
# app = Flask(__name__)

# # Set up logging
# log_file = setup_logger()
# log_app_event("startup", f"Application started, logging to {log_file}")

# # Configure upload folder
# UPLOAD_FOLDER = 'static/uploads'
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)
#     log_app_event("directory_creation", f"Created upload directory: {UPLOAD_FOLDER}")
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# @app.route('/')
# def index():
#     log_app_event("page_access", "Index page accessed")
#     return render_template('index.html')

# @app.route('/process', methods=['POST'])
# def process_image():
#     try:
#         # Check if image file is uploaded
#         if 'image_file' not in request.files:
#             log_error("missing_file", "No image file provided in request")
#             return jsonify({
#                 'status': 'error',
#                 'message': 'No image file provided'
#             })
        
#         file = request.files['image_file']
#         if file.filename == '':
#             log_error("empty_filename", "Empty filename provided")
#             return jsonify({
#                 'status': 'error',
#                 'message': 'No image selected'
#             })
        
#         filename = secure_filename(file.filename)
#         log_app_event("file_upload", f"File uploaded: {filename}")
        
#         # Read file data into memory
#         file_bytes = file.read()
#         nparr = np.frombuffer(file_bytes, np.uint8)
        
#         # Process the uploaded image with OpenCV
#         log_image_processing(filename, "image_decoding", "start")
#         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#         if img is None:
#             log_error("decode_failure", f"Failed to decode image: {filename}")
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Failed to decode image'
#             })
#         log_image_processing(filename, "image_decoding", "complete")
        
#         # Save the original image
#         original_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input.jpg')
#         cv2.imwrite(original_path, img)
#         log_app_event("file_save", f"Original image saved to {original_path}")
        
#         # ------------- - Process the image - ---------------------------
#         log_app_event("processing_start", f"Starting image processing for {filename}")
#         report, processed_img = process_pipeline(img, filename)
#         processed_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.jpg')
#         cv2.imwrite(processed_path, processed_img)
#         log_app_event("processing_complete", f"Processing complete, result saved to {processed_path}")
        
#         # ------------- - ----------------- - ---------------------------
        
#         # Convert images to base64 for display
#         log_image_processing(filename, "base64_conversion", "start")
#         with open(original_path, 'rb') as f:
#             original_base64 = base64.b64encode(f.read()).decode('utf-8')
        
#         with open(processed_path, 'rb') as f:
#             processed_base64 = base64.b64encode(f.read()).decode('utf-8')
#         log_image_processing(filename, "base64_conversion", "complete")
        
#         log_app_event("request_success", f"Successfully processed image: {filename}")
#         return jsonify({
#             'status': 'success',
#             'message': report,
#             'original_image': original_base64,
#             'processed_image': processed_base64,
#             'log': f'Uploaded image: {filename}\nProcessing: Caries Segmenting\nProcessing complete'
#         })
    
#     except Exception as e:
#         error_msg = f'Error processing image: {str(e)}'
#         log_error("processing_error", "Unhandled exception in process_image endpoint", e)
#         return jsonify({
#             'status': 'error',
#             'message': error_msg
#         })

# @app.route('/evaluate', methods=['POST'])
# def evaluate_image():
#     try:
#         # Check if image files are uploaded
#         if 'image_file' not in request.files or 'reference_file' not in request.files:
#             log_error("missing_file", "Missing image or reference file in request")
#             return jsonify({
#                 'status': 'error',
#                 'message': 'Both image and reference files are required'
#             })
        
#         # Get the files
#         input_file = request.files['image_file']
#         reference_file = request.files['reference_file']
        
#         # Read the input file
#         input_bytes = input_file.read()
#         input_nparr = np.frombuffer(input_bytes, np.uint8)
#         input_img = cv2.imdecode(input_nparr, cv2.IMREAD_COLOR)
        
#         # Read the reference file - make sure it's grayscale for the ground truth
#         ref_bytes = reference_file.read()
#         ref_nparr = np.frombuffer(ref_bytes, np.uint8)
#         gt_img_color = cv2.imdecode(ref_nparr, cv2.IMREAD_COLOR)
        
#         # Convert ground truth to grayscale if it's RGB
#         if len(gt_img_color.shape) == 3:
#             gt_img = cv2.cvtColor(gt_img_color, cv2.COLOR_BGR2GRAY)
#         else:
#             gt_img = gt_img_color
        
#         # Process the input image
#         log_app_event("evaluation", "Processing input image")
#         results = analyzer.analyze_image(input_img)
        
#         # Get the list of tooth masks
#         log_app_event("evaluation", "Getting tooth masks")
#         list_of_masks = results['teeth_masks']
        
#         # Get the caries mask (predicted) - ensure it's grayscale
#         pred_roi = results['caries_mask']
        
#         # Ensure both masks have the same dimensions
#         if pred_roi.shape != gt_img.shape:
#             gt_img = cv2.resize(gt_img, (pred_roi.shape[1], pred_roi.shape[0]))
        
#         # Run evaluation
#         log_app_event("evaluation", "Running evaluation")
#         eval_results = evaluate_caries_detection_fixed(pred_roi, gt_img, list_of_masks)
        
#         # Generate report
#         log_app_event("evaluation", "Generating report")
#         report = generate_enhanced_report(eval_results)
        
#         # Generate visualization
#         log_app_event("evaluation", "Creating visualization")
        
#         # Create a temporary filename with UUID to avoid conflicts
#         temp_filename = f"eval_report_{uuid.uuid4().hex}.png"
#         temp_filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        
#         # Generate and save the visualization
#         fig = visualize_enhanced_comparison(input_img, pred_roi, gt_img, list_of_masks)
#         fig.savefig(temp_filepath, format='png', bbox_inches='tight', dpi=100)
#         plt.close(fig)
        
#         # Also save to buffer for backward compatibility
#         buffer = io.BytesIO()
#         fig = visualize_enhanced_comparison(input_img, pred_roi, gt_img, list_of_masks)
#         fig.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
#         buffer.seek(0)
#         img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
#         plt.close(fig)
        
#         return jsonify({
#             'status': 'success',
#             'report': report,
#             'visualization': img_str,
#             'visualization_path': f'/static/uploads/{temp_filename}'  # Add this new field
#         })
    
#     except Exception as e:
#         error_msg = f'Error in evaluation: {str(e)}'
#         log_error("evaluation_error", "Unhandled exception in evaluate_image endpoint", e)
#         import traceback
#         tb = traceback.format_exc()
#         log_error("evaluation_traceback", tb)
        
#         return jsonify({
#             'status': 'success',
#             'report': report,
#             'visualization': img_str,
#             'visualization_path': f'/static/uploads/{temp_filename}',
#             'temp_filename': temp_filename  # Add this line
#         })
    
# @app.route('/logs')
# def list_logs():
#     """Route to list all available log files."""
#     log_app_event("page_access", "Logs listing page accessed")
#     log_dir = 'logs'
#     if not os.path.exists(log_dir):
#         return "No logs directory found."
    
#     log_files = sorted([f for f in os.listdir(log_dir) if f.endswith('.log')], reverse=True)
#     html = '<h1>Available Log Files</h1>'
#     html += '<ul>'
#     for log_file in log_files:
#         html += f'<li><a href="/logs/view/{log_file}">{log_file}</a></li>'
#     html += '</ul>'
#     return html

# @app.route('/logs/view/<filename>')
# def view_log(filename):
#     """Route to view a specific log file."""
#     log_app_event("log_view", f"Log file viewed: {filename}")
#     log_dir = 'logs'
#     file_path = os.path.join(log_dir, filename)
    
#     if not os.path.exists(file_path) or not filename.endswith('.log'):
#         return "Log file not found or invalid filename."
    
#     try:
#         with open(file_path, 'r') as f:
#             content = f.read()
        
#         # Format log for HTML display
#         content = content.replace('\n', '<br>')
#         html = f'<h1>Log File: {filename}</h1>'
#         html += f'<a href="/logs">Back to logs list</a>'
#         html += f'<div style="margin-top: 20px; font-family: monospace; white-space: pre-wrap;">{content}</div>'
#         return html
#     except Exception as e:
#         log_error("log_view_error", f"Error viewing log file {filename}", e)
#         return f"Error reading log file: {str(e)}"

# @app.route('/logs/download/<filename>')
# def download_log(filename):
#     """Route to download a specific log file."""
#     log_app_event("log_download", f"Log file downloaded: {filename}")
#     log_dir = 'logs'
    
#     if not filename.endswith('.log'):
#         return "Invalid log filename."
    
#     return send_from_directory(directory=log_dir, path=filename, as_attachment=True)    

# @app.errorhandler(404)
# def page_not_found(e):
#     """Handle 404 errors."""
#     log_error("http_404", f"Page not found: {request.path}")
#     return jsonify({
#         'status': 'error',
#         'message': 'Page not found'
#     }), 404

# @app.errorhandler(500)
# def server_error(e):
#     """Handle 500 errors."""
#     log_error("http_500", f"Server error on {request.path}", e)
#     return jsonify({
#         'status': 'error',
#         'message': 'Internal server error occurred'
#     }), 500

# # This function will be called when the app is shutting down
# @app.teardown_appcontext
# def log_shutdown(exception=None):
#     if exception:
#         log_error("shutdown_error", "Application shutdown with error", exception)
#     else:
#         log_app_event("shutdown", "Application shutdown normally")
    
#     # Clean up all temporary evaluation report files
#     try:
#         upload_folder = app.config.get('UPLOAD_FOLDER', 'static/uploads')
#         if os.path.exists(upload_folder):
#             # Count how many files were cleaned up
#             cleanup_count = 0
            
#             # Get all files in the upload folder
#             for filename in os.listdir(upload_folder):
#                 # Check if it's a temporary evaluation report file
#                 if filename.startswith('eval_report_') and filename.endswith('.png'):
#                     file_path = os.path.join(upload_folder, filename)
#                     # Delete the file
#                     os.remove(file_path)
#                     cleanup_count += 1
            
#             if cleanup_count > 0:
#                 log_app_event("cleanup", f"Cleaned up {cleanup_count} temporary evaluation report files during shutdown")
#     except Exception as e:
#         log_error("cleanup_error", "Failed to clean up temporary files during shutdown", e)
    
# if __name__ == '__main__':
#     log_app_event("server_start", "Starting Flask server on 0.0.0.0:5000")
#     app.run(host='0.0.0.0', port=5000, debug=False)


from llm_bridge import format_data_for_llm, ask_ollama  #add new Import


from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import cv2
import numpy as np
import base64
import re
import io
import uuid
import matplotlib.pyplot as plt
from datetime import datetime
from werkzeug.utils import secure_filename
from dental_analysis_tool import DentalAnalyzer
from evaluation import evaluate_caries_detection_fixed, generate_enhanced_report, visualize_enhanced_comparison

# Import logging utilities
import logging
from logger_utils import setup_logger, log_image_processing, log_app_event, log_error

####################################################################################################
############################# ML Section ###########################################################
####################################################################################################

# Initialize the analyzer with default or custom model paths
analyzer = DentalAnalyzer(
    tooth_detection_path='weights/Tooth_detect_pano_20250319.pt',
    caries_segmentation_path='weights/Caries_seg_single_20250319.pth',
    tooth_recognition_path='weights/Tooth_seg_pano_20250319.pt',
    refined_tooth_seg_path='weights/Tooth_seg_crop_20250424.pth'
)

## Process the Image function  ----------------------------------------
def process_pipeline(pano_img, filename):
    try:
        log_image_processing(filename, "analyzer.analyze_image", "start")
        results = analyzer.analyze_image(pano_img)
        log_image_processing(filename, "analyzer.analyze_image", "complete")

        report = results['report']
        vis = results['caries_visualization']
        refined_regions = results.get('refined_regions', [])
        teeth_with_caries = results.get('teeth_with_caries', {})
        teeth_masks = results.get('teeth_masks', [])

        #add : pull Prob
        tooth_probs = results.get('tooth_mean_probs', {})
        
        return report, vis, refined_regions, teeth_with_caries, teeth_masks, tooth_probs #add tooth_probs
    except Exception as e:
        log_error("process_pipeline", f"Failed to process image {filename}", e)
        raise

####################################################################################################
############################# App Section ##########################################################
####################################################################################################

# Initialize the Flask app
app = Flask(__name__)

# Set up logging
log_file = setup_logger()
log_app_event("startup", f"Application started, logging to {log_file}")

# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    log_app_event("directory_creation", f"Created upload directory: {UPLOAD_FOLDER}")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    log_app_event("page_access", "Index page accessed")
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_image():
    try:
        if 'image_file' not in request.files:
            log_error("missing_file", "No image file provided in request")
            return jsonify({'status': 'error','message': 'No image file provided'})
        
        file = request.files['image_file']
        if file.filename == '':
            log_error("empty_filename", "Empty filename provided")
            return jsonify({'status': 'error','message': 'No image selected'})

        filename = secure_filename(file.filename)
        log_app_event("file_upload", f"File uploaded: {filename}")

        file_bytes = file.read()
        nparr = np.frombuffer(file_bytes, np.uint8)
        log_image_processing(filename, "image_decoding", "start")
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            log_error("decode_failure", f"Failed to decode image: {filename}")
            return jsonify({'status': 'error','message': 'Failed to decode image'})
        log_image_processing(filename, "image_decoding", "complete")

        original_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input.jpg')
        cv2.imwrite(original_path, img)
        log_app_event("file_save", f"Original image saved to {original_path}")


        log_app_event("processing_start", f"Starting image processing for {filename}")
        
        report, processed_img, refined_regions, teeth_with_caries, teeth_masks, tooth_probs = process_pipeline(img, filename) #add tooth_probs
        
        processed_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.jpg')
        cv2.imwrite(processed_path, processed_img)
        log_app_event("processing_complete", f"Processing complete, result saved to {processed_path}")


        # ==================================================================================
        #add Start: Call LLM Bridge
        # ==================================================================================
        try:
            log_app_event("ai_bridge", "Generating AI Report with Ollama...")
            
            # เนื่องจากเราไม่ได้แก้ process_pipeline ให้ส่งค่า probs มา (เพื่อความปลอดภัย)
            # เราจะสร้าง dict ว่างๆ ไปก่อน (Code จะทำงานได้ปกติ แค่ไม่มี % ความมั่นใจโชว์)
            dummy_probs = {} 
            
            # 1. แปลงข้อมูลเป็นข้อความ
            formatted_text = format_data_for_llm(teeth_with_caries, dummy_probs)
            
            # 2. ส่งให้ Ollama เขียน Report
            ai_report = ask_ollama(formatted_text)
            
        except Exception as e:
            # Safety Net: ถ้าส่วน AI พัง ให้กลับไปใช้ Report แบบเดิม โปรแกรมจะไม่ล่ม
            log_error("ai_bridge_error", "Failed to generate AI report", e)
            print(f"AI Bridge Error: {e}")
            ai_report = report 
        # ==================================================================================
        # [ส่วนที่เพิ่มใหม่] สิ้นสุด
        # ==================================================================================


        log_image_processing(filename, "base64_conversion", "start")
        with open(original_path, 'rb') as f:
            original_base64 = base64.b64encode(f.read()).decode('utf-8')
        with open(processed_path, 'rb') as f:
            processed_base64 = base64.b64encode(f.read()).decode('utf-8')
        log_image_processing(filename, "base64_conversion", "complete")
        
        log_app_event("request_success", f"Successfully processed image: {filename}")
        
        return jsonify({
            'status': 'success',
            
            # [แก้ตรงนี้] เปลี่ยนจาก 'message': report เป็น 'message': ai_report
            'message': ai_report, 
            
            'original_image': original_base64,
            'processed_image': processed_base64,
            'teeth_with_caries': teeth_with_caries,
            'refined_regions_count': len(refined_regions),
            'teeth_mask_count': len(teeth_masks),
            'log': f'Uploaded image: {filename}\nProcessing: Caries Segmenting\nProcessing complete'
        })

    except Exception as e:
        error_msg = f'Error processing image: {str(e)}'
        log_error("processing_error", "Unhandled exception in process_image endpoint", e)
        return jsonify({'status': 'error','message': error_msg})

if __name__ == '__main__':
    log_app_event("server_start", "Starting Flask server on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
