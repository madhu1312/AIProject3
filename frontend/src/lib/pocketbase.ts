import PocketBase from 'pocketbase';

// PocketBase instance - connects to local PocketBase server
export const pb = new PocketBase('http://127.0.0.1:8090');

// Disable auto cancellation for multiple requests
pb.autoCancellation(false);

export default pb;
