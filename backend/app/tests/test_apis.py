from __future__ import annotations

import httpx
from loguru import logger
from PIL import Image, ImageDraw
import os

BASE_URL = "http://127.0.0.1:8765"
TEST_USER_ID = "test_user"

# --- Helper function to create dummy invoice image ---
def create_dummy_invoice_image(filename="dummy_invoice.png") -> str:
    """Creates a dummy invoice image and returns its file path."""
    try:
        img = Image.new('RGB', (600, 800), color = (255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((10,10), "Invoice Details:", fill=(0,0,0))
        d.text((10,40), "Vendor: Test Vendor", fill=(0,0,0))
        d.text((10,70), "Invoice Number: INV-12345", fill=(0,0,0))
        d.text((10,100), "Date: 2023-10-26", fill=(0,0,0))
        d.text((10,130), "Total: $100.00", fill=(0,0,0))

        filepath = os.path.join(os.path.dirname(__file__), filename)
        img.save(filepath)
        logger.info(f"Dummy invoice image created at: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error creating dummy image: {e}")
        return ""

# --- Test cases ---

def test_health_check():
    """Test the GET /health endpoint."""
    logger.info("--- Testing GET /health ---")
    try:
        response = httpx.get(f"{BASE_URL}/health")
        if response.status_code == 200 and response.json() == {"status": "ok"}:
            logger.debug(f"Response: {response.json()}")
            logger.info("PASS: GET /health")
            return True
        else:
            logger.error(f"FAIL: GET /health - Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"FAIL: GET /health - Exception: {e}")
        return False


def test_extract_upload_and_get():
    """Test POST /extract/upload and GET /extract/{extraction_id} endpoints."""
    logger.info("--- Testing POST /extract/upload and GET /extract/{extraction_id} ---")

    # Create a dummy invoice image if it doesn't exist
    image_path = create_dummy_invoice_image()
    if not image_path:
        logger.error("FAIL: POST /extract/upload - Could not create dummy image.")
        return False, None

    try:
        with open(image_path, "rb") as f:
            files = {"file": (os.path.basename(image_path), f, "image/png")}
            response = httpx.post(f"{BASE_URL}/extract/upload", files=files, timeout=60.0) # Increased timeout for potentially longer processing

        if response.status_code == 200:
            extraction_data = response.json()
            logger.debug(f"Response: {extraction_data}")
            extraction_id = extraction_data.get("extraction_id")
            if extraction_id:
                logger.info("PASS: POST /extract/upload")

                # Test GET /extract/{extraction_id}
                get_response = httpx.get(f"{BASE_URL}/extract/{extraction_id}")
                if get_response.status_code == 200:
                    extracted_data = get_response.json()
                    logger.debug(f"GET Response: {extracted_data}")
                    logger.info("PASS: GET /extract/{extraction_id}")
                    return True, extraction_id
                else:
                    logger.error(f"FAIL: GET /extract/{extraction_id} - Status: {get_response.status_code}, Response: {get_response.text}")
                    return True, None # POST passed, GET failed
            else:
                logger.error("FAIL: POST /extract/upload - extraction_id not found in response.")
                return False, None
        else:
            logger.error(f"FAIL: POST /extract/upload - Status: {response.status_code}, Response: {response.text}")
            return False, None
    except Exception as e:
        logger.error(f"FAIL: POST /extract/upload - Exception: {e}")
        return False, None

def test_update_extraction():
    """Test PUT /extract/{extraction_id} endpoint."""
    logger.info("--- Testing PUT /extract/{extraction_id} ---")

    # First, create an extraction to get an ID
    post_success, extraction_id = test_extract_upload_and_get()
    if not post_success or not extraction_id:
        logger.error("FAIL: PUT /extract/{extraction_id} - Pre-request failed: Could not get extraction ID.")
        return False

    update_data = {
        "vendor_name": "Test Vendor Updated"
    }

    try:
        response = httpx.put(f"{BASE_URL}/extract/{extraction_id}", json=update_data)
        if response.status_code == 200:
            updated_data = response.json()
            logger.debug(f"Response: {updated_data}")
            if updated_data.get("vendor_name") == "Test Vendor Updated":
                logger.info("PASS: PUT /extract/{extraction_id}")
                return True
            else:
                logger.error(f"FAIL: PUT /extract/{extraction_id} - Vendor name not updated correctly.")
                return False
        else:
            logger.error(f"FAIL: PUT /extract/{extraction_id} - Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"FAIL: PUT /extract/{extraction_id} - Exception: {e}")
        return False

def test_get_history():
    """Test GET /history endpoint."""
    logger.info("--- Testing GET /history ---")
    try:
        response = httpx.get(f"{BASE_URL}/history?user_id={TEST_USER_ID}")
        if response.status_code == 200:
            history_data = response.json()
            logger.debug(f"Response: {history_data}")
            if isinstance(history_data, list):
                logger.info("PASS: GET /history")
                return True
            else:
                logger.error("FAIL: GET /history - Response is not a list.")
                return False
        else:
            logger.error(f"FAIL: GET /history - Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"FAIL: GET /history - Exception: {e}")
        return False

def test_export_extraction():
    """Test POST /export endpoint for CSV and Excel formats."""
    logger.info("--- Testing POST /export ---")

    # First, create an extraction to get an ID
    post_success, extraction_id = test_extract_upload_and_get() # Reuse the function that creates an extraction
    if not post_success or not extraction_id:
        logger.error("FAIL: POST /export - Pre-request failed: Could not get extraction ID.")
        return False

    # Test CSV export
    csv_downloaded = False
    try:
        response_csv = httpx.post(f"{BASE_URL}/export?format=csv", json={"extraction_ids": [extraction_id]})
        if response_csv.status_code == 200 and "text/csv" in response_csv.headers.get("content-type", ""):
            logger.debug(f"CSV Export Response Headers: {response_csv.headers}")
            logger.info("PASS: POST /export (CSV)")
            csv_downloaded = True
        else:
            logger.error(f"FAIL: POST /export (CSV) - Status: {response_csv.status_code}, Response: {response_csv.text}")
    except Exception as e:
        logger.error(f"FAIL: POST /export (CSV) - Exception: {e}")

    # Test Excel export
    excel_downloaded = False
    try:
        response_excel = httpx.post(f"{BASE_URL}/export?format=excel", json={"extraction_ids": [extraction_id]})
        if response_excel.status_code == 200 and "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response_excel.headers.get("content-type", ""):
            logger.debug(f"Excel Export Response Headers: {response_excel.headers}")
            logger.info("PASS: POST /export (Excel)")
            excel_downloaded = True
        else:
            logger.error(f"FAIL: POST /export (Excel) - Status: {response_excel.status_code}, Response: {response_excel.text}")
    except Exception as e:
        logger.error(f"FAIL: POST /export (Excel) - Exception: {e}")

    return csv_downloaded and excel_downloaded


def run_tests():
    """Runs all defined tests and saves results."""
    results = {"passed": 0, "failed": 0}
    test_log = []

    def log_test_result(test_name, passed, response_data=None, error=None):
        status = "PASS" if passed else "FAIL"
        result_str = f"{test_name}: {status}\n"
        if response_data is not None:
            result_str += f"Response: {response_data}\n"
        if error:
            result_str += f"Error: {error}\n"
        test_log.append(result_str)
        if passed:
            results["passed"] += 1
        else:
            results["failed"] += 1

    # --- Execute tests ---
    # Health Check
    health_passed = test_health_check()
    log_test_result("GET /health", health_passed)

    # Extract Upload and Get
    upload_passed, extraction_id_for_next_tests = test_extract_upload_and_get()
    log_test_result("POST /extract/upload", upload_passed)

    # Update Extraction
    update_passed = False
    if upload_passed and extraction_id_for_next_tests:
        update_passed = test_update_extraction()
        log_test_result("PUT /extract/{extraction_id}", update_passed)
    else:
        log_test_result("PUT /extract/{extraction_id}", False, error="Skipped due to previous test failure or missing extraction ID.")

    # Get History
    history_passed = test_get_history()
    log_test_result("GET /history", history_passed)

    # Export Extraction
    export_passed = False
    if upload_passed and extraction_id_for_next_tests:
        export_passed = test_export_extraction()
        log_test_result("POST /export", export_passed)
    else:
        log_test_result("POST /export", False, error="Skipped due to previous test failure or missing extraction ID.")

    # --- Save results to file ---
    output_filename = "backend/app/tests/test_results.txt"
    try:
        with open(output_filename, "w") as f:
            f.write("--- API Test Results ---")
            f.write(f"\nTotal Tests: {results['passed'] + results['failed']}")
            f.write(f"\nPassed: {results['passed']}")
            f.write(f"\nFailed: {results['failed']}")
            f.write("\n\n--- Detailed Results ---")
            for log in test_log:
                f.write(f"\n{log}")
        logger.info(f"Test results saved to {output_filename}")
    except Exception as e:
        logger.error(f"Error saving test results to {output_filename}: {e}")

    # --- Print summary ---
    logger.info("--- Test Summary ---")
    logger.info(f"Total APIs tested: {results['passed'] + results['failed']}")
    logger.info(f"Passed: {results['passed']}")
    logger.info(f"Failed: {results['failed']}")

    if results["failed"] > 0:
        logger.warning("--- Failed APIs ---")

if __name__ == "__main__":
    run_tests()
