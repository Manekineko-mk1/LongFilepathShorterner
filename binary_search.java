public class binary_search {
    
    // binary search algorithm works by repeatedly dividing the search interval in half, 
    // for example: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    // and we search for 7
    // we start at the middle, which is 5, 
    // then we compare 7 with 5, since 7 > 5, we search the right half, which is [6, 7, 8, 9, 10]
    // then we start at the middle again, which is 8, and we compare 7 with 8, since 7 < 8, we search the left half, which is [6, 7]
    // then we start at the middle again, which is 7, and we compare 7 with 7, since 7 == 7, we found it!
    
    // implement binary search
    public static int binarySearch(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;
        
        while (left <= right) {
            // int mid = (left + right) / 2; // may cause overflow, example: left = 2147483647, right = 2147483647 -> mid = -1
            int mid = left + (right - left) / 2; // better
            if (arr[mid] == target) {
                return mid;
            }
            else if (arr[mid] < target) {
                left = mid + 1; // search right half
            }
            else {
                right = mid - 1; // search left half
            }
        }
        
        return -1;
    }
    
}
