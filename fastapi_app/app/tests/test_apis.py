# test_apis.py

import httpx
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
        print(f"Dummy invoice image created at: {filepath}")
        return filepath
    except Exception as e:
        print(f"Error creating dummy image: {e}")
        return ""

# --- Test cases ---

def test_health_check():
    """Test the GET /health endpoint."""
    print("\n--- Testing GET /health ---")
    try:
        response = httpx.get(f"{BASE_URL}/health")
        if response.status_code == 200 and response.json() == {"status": "ok"}:
            print("Response: ", response.json())
            print("PASS: GET /health ✅")
            return True
        else:
            print(f"FAIL: GET /health ❌ - Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print(f"FAIL: GET /health ❌ - Exception: {e}")
        return False


def test_extract_upload_and_get():
    """Test POST /extract/upload and GET /extract/{extraction_id} endpoints."""
    print("\n--- Testing POST /extract/upload and GET /extract/{extraction_id} ---")

    # Create a dummy invoice image if it doesn't exist
    image_path = create_dummy_invoice_image()
    if not image_path:
        print("FAIL: POST /extract/upload ❌ - Could not create dummy image.")
        return False, None

    try:
        with open(image_path, "rb") as f:
            files = {"file": (os.path.basename(image_path), f, "image/png")}
            response = httpx.post(f"{BASE_URL}/extract/upload", files=files, timeout=60.0) # Increased timeout for potentially longer processing

        if response.status_code == 200:
            extraction_data = response.json()
            print("Response: ", extraction_data)
            extraction_id = extraction_data.get("extraction_id")
            if extraction_id:
                print("PASS: POST /extract/upload ✅")

                # Test GET /extract/{extraction_id}
                get_response = httpx.get(f"{BASE_URL}/extract/{extraction_id}")
                if get_response.status_code == 200:
                    extracted_data = get_response.json()
                    print("GET Response: ", extracted_data)
                    print("PASS: GET /extract/{extraction_id} ✅")
                    return True, extraction_id
                else:
                    print(f"FAIL: GET /extract/{extraction_id} ❌ - Status: {get_response.status_code}, Response: {get_response.text}")
                    return True, None # POST passed, GET failed
            else:
                print("FAIL: POST /extract/upload ❌ - extraction_id not found in response.")
                return False, None
        else:
            print(f"FAIL: POST /extract/upload ❌ - Status: {response.status_code}, Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"FAIL: POST /extract/upload ❌ - Exception: {e}")
        return False, None

def test_update_extraction():
    """Test PUT /extract/{extraction_id} endpoint."""
    print("\n--- Testing PUT /extract/{extraction_id} ---")

    # First, create an extraction to get an ID
    post_success, extraction_id = test_extract_upload_and_get()
    if not post_success or not extraction_id:
        print("FAIL: PUT /extract/{extraction_id} ❌ - Pre-request failed: Could not get extraction ID.")
        return False

    update_data = {
        "vendor_name": "Test Vendor Updated"
    }

    try:
        response = httpx.put(f"{BASE_URL}/extract/{extraction_id}", json=update_data)
        if response.status_code == 200:
            updated_data = response.json()
            print("Response: ", updated_data)
            if updated_data.get("vendor_name") == "Test Vendor Updated":
                print("PASS: PUT /extract/{extraction_id} ✅")
                return True
            else:
                print(f"FAIL: PUT /extract/{extraction_id} ❌ - Vendor name not updated correctly.")
                return False
        else:
            print(f"FAIL: PUT /extract/{extraction_id} ❌ - Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print(f"FAIL: PUT /extract/{extraction_id} ❌ - Exception: {e}")
        return False

def test_get_history():
    """Test GET /history endpoint."""
    print("\n--- Testing GET /history ---")
    try:
        response = httpx.get(f"{BASE_URL}/history?user_id={TEST_USER_ID}")
        if response.status_code == 200:
            history_data = response.json()
            print("Response: ", history_data)
            if isinstance(history_data, list):
                print("PASS: GET /history ✅")
                return True
            else:
                print("FAIL: GET /history ❌ - Response is not a list.")
                return False
        else:
            print(f"FAIL: GET /history ❌ - Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print(f"FAIL: GET /history ❌ - Exception: {e}")
        return False

def test_export_extraction():
    """Test POST /export endpoint for CSV and Excel formats."""
    print("\n--- Testing POST /export ---")

    # First, create an extraction to get an ID
    post_success, extraction_id = test_extract_upload_and_get() # Reuse the function that creates an extraction
    if not post_success or not extraction_id:
        print("FAIL: POST /export ❌ - Pre-request failed: Could not get extraction ID.")
        return False

    # Test CSV export
    try:
        response_csv = httpx.post(f"{BASE_URL}/export?format=csv", json={"extraction_id": extraction_id})
        if response_csv.status_code == 200 and "text/csv" in response_csv.headers.get("content-type", ""):
            print("CSV Export Response Headers: ", response_csv.headers)
            print("PASS: POST /export (CSV) ✅")
            csv_downloaded = True
        else:
            print(f"FAIL: POST /export (CSV) ❌ - Status: {response_csv.status_code}, Response: {response_csv.text}")
            csv_downloaded = False
    except Exception as e:
        print(f"FAIL: POST /export (CSV) ❌ - Exception: {e}")
        csv_downloaded = False

    # Test Excel export
    try:
        response_excel = httpx.post(f"{BASE_URL}/export?format=excel", json={"extraction_id": extraction_id})
        if response_excel.status_code == 200 and "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response_excel.headers.get("content-type", ""):
            print("Excel Export Response Headers: ", response_excel.headers)
            print("PASS: POST /export (Excel) ✅")
            excel_downloaded = True
        else:
            print(f"FAIL: POST /export (Excel) ❌ - Status: {response_excel.status_code}, Response: {response_excel.text}")
            excel_downloaded = False
    except Exception as e:
        print(f"FAIL: POST /export (Excel) ❌ - Exception: {e}")
        excel_downloaded = False

    return csv_downloaded and excel_downloaded


def run_tests():
    """Runs all defined tests and saves results."""
    results = {"passed": 0, "failed": 0}
    test_log = []

    def log_test_result(test_name, passed, response_data=None, error=None):
        status = "PASS ✅" if passed else "FAIL ❌"
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
    # Note: This test depends on the health check passing, but we run it regardless.
    # The function itself returns success/failure and the extraction_id for subsequent tests.
    upload_passed, extraction_id_for_next_tests = test_extract_upload_and_get()
    log_test_result("POST /extract/upload", upload_passed)
    # The GET part is handled within test_extract_upload_and_get, so we log its result there.

    # Update Extraction
    update_passed = False
    if upload_passed and extraction_id_for_next_tests: # Only run update if upload was successful and we have an ID
        update_passed = test_update_extraction()
        log_test_result("PUT /extract/{extraction_id}", update_passed)
    else:
        log_test_result("PUT /extract/{extraction_id}", False, error="Skipped due to previous test failure or missing extraction ID.")

    # Get History
    history_passed = test_get_history()
    log_test_result("GET /history", history_passed)

    # Export Extraction
    export_passed = False
    if upload_passed and extraction_id_for_next_tests: # Only run export if upload was successful and we have an ID
        export_passed = test_export_extraction()
        log_test_result("POST /export", export_passed)
    else:
        log_test_result("POST /export", False, error="Skipped due to previous test failure or missing extraction ID.")

    # --- Save results to file ---
    output_filename = "fastapi_app/app/tests/test_results.txt"
    try:
        with open(output_filename, "w") as f:
            f.write("--- API Test Results ---")
            f.write(f"\nTotal Tests: {results['passed'] + results['failed']}")
            f.write(f"\nPassed: {results['passed']} ✅")
            f.write(f"\nFailed: {results['failed']} ❌")
            f.write("\n\n--- Detailed Results ---")
            for log in test_log:
                f.write(f"\n{log}")
        print(f"\nTest results saved to {output_filename}")
    except Exception as e:
        print(f"\nError saving test results to {output_filename}: {e}")

    # --- Print summary ---
    print("\n--- Test Summary ---")
    print(f"Total APIs tested: {results['passed'] + results['failed']}")
    print(f"Passed: {results['passed']} ✅")
    print(f"Failed: {results['failed']} ❌")

    if results["failed"] > 0:
        print("\n--- Failed APIs ---")
        # Logic to list failed APIs will be here after executing tests

if __name__ == "__main__":
    run_tests()
