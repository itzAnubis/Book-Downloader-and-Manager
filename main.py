from app_.util.storage.storage_handle import R2Storage
import os

def test_r2_storage():
    """Test all R2 storage operations"""
    
    # Initialize the R2 client
    r2 = R2Storage(
        bucket_name='book-storage'  # Replace with your actual bucket name
    )
    
    print("=" * 50)
    print("Testing Cloudflare R2 Storage")
    print("=" * 50)
    
    # Test 1: Upload a file
    print("\n1. Testing File Upload...")
    with open('test_file.txt', 'w') as f:
        f.write('Hello from Cloudflare R2!')
    
    success = r2.upload_file('test_file.txt', 'test_file.txt')
    print(f"   Upload Status: {'✓ Success' if success else '✗ Failed'}")
    
    # Test 2: Check if object exists
    print("\n2. Testing Object Existence Check...")
    exists = r2.object_exists('test_file.txt')
    print(f"   Object Exists: {'✓ Yes' if exists else '✗ No'}")
    
    # Test 3: List objects
    print("\n3. Testing List Objects...")
    objects = r2.list_objects()
    print(f"   Objects in bucket: {len(objects)}")
    for obj in objects:
        print(f"      - {obj['Key']} ({obj['Size']} bytes)")
    
    # Test 4: Download a file
    print("\n4. Testing File Download...")
    success = r2.download_file('test_file.txt', 'downloaded_test_file.txt')
    print(f"   Download Status: {'✓ Success' if success else '✗ Failed'}")
    
    # Verify downloaded content
    if os.path.exists('downloaded_test_file.txt'):
        with open('downloaded_test_file.txt', 'r') as f:
            content = f.read()
        print(f"   Downloaded Content: {content}")
    
    # Test 5: Get object as bytes
    print("\n5. Testing Get Object (Bytes)...")
    data = r2.get_object('test_file.txt')
    if data:
        print(f"   Object Content: {data.decode('utf-8')}")
    
    # Test 6: Put object directly (without file)
    print("\n6. Testing Put Object (Bytes)...")
    success = r2.put_object(
        data=b'Direct upload content',
        object_name='direct_upload.txt',
        content_type='text/plain'
    )
    print(f"   Put Object Status: {'✓ Success' if success else '✗ Failed'}")
    
    # Test 7: Delete objects
    print("\n7. Testing Delete Objects...")
    success1 = r2.delete_object('test_file.txt')
    success2 = r2.delete_object('direct_upload.txt')
    print(f"   Delete test_file.txt: {'✓ Success' if success1 else '✗ Failed'}")
    print(f"   Delete direct_upload.txt: {'✓ Success' if success2 else '✗ Failed'}")
    
    # Cleanup local test files
    if os.path.exists('test_file.txt'):
        os.remove('test_file.txt')
    if os.path.exists('downloaded_test_file.txt'):
        os.remove('downloaded_test_file.txt')
    
    print("\n" + "=" * 50)
    print("All Tests Completed!")
    print("=" * 50)


if __name__ == '__main__':
    test_r2_storage()