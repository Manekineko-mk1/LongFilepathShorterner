public class test_java {



    // Reverse a string without using recursion
    public static String reverseStringIterative(String str) {
        StringBuilder sb = new StringBuilder();
        for (int i = str.length() - 1; i >= 0; i--) {
            sb.append(str.charAt(i)); // Append characters in reverse order
        }
        return sb.toString();
    }

    // Reverse a string using recursion
    public static String reverseString(String str) {
        if (str.isEmpty())
            return str;
        return reverseString(str.substring(1)) + str.charAt(0);
    }

    // Check if a int is a palindrome
    // 121 -> true because 121 in reverse is 121
    // 123 -> false because 123 in reverse is 321
    // the idea is to reverse the number and compare it with the original number
    // we start with num = 121, reversedNum = 0, originalNum = 121
    // 1st iteration:
    // - we get the remainder of num % 10, num = 121, remainder = 1
    // - we multiply reversedNum by 10 and add the remainder (1), reversedNum = 0 * 10 + 1 = 1
    // - we divide num by 10, num = 121 / 10 = 12
    // 2nd iteration:
    // - we get the remainder of num % 10, num = 12, remainder = 2
    // - we multiply reversedNum by 10 and add the remainder (2), reversedNum = 1 * 10 + 2 = 12
    // - we divide num by 10, num = 12 / 10 = 1
    // 3rd iteration:
    // - we get the remainder of num % 10, num = 1, remainder = 1
    // - we multiply reversedNum by 10 and add the remainder (1), reversedNum = 12 * 10 + 1 = 121
    // - we divide num by 10, num = 1 / 10 = 0
    // num is 0, we exit the while loop
    // we return originalNum == reversedNum, 121 == 121, true
    public static boolean isPalindrome(int num) {
        int reversedNum = 0;
        int originalNum = num;

        while (num != 0) {
            int remainder = num % 10;
            reversedNum = reversedNum * 10 + remainder;
            num /= 10;
        }

        return originalNum == reversedNum;
    }


    // Check if a string is a palindrome, case insensitive
    public static boolean isPalindrome(String str) {
        str = str.toLowerCase(); // Convert to lowercase
        
        int left = 0;
        int right = str.length() - 1;

        while (left < right) {
            if (str.charAt(left) != str.charAt(right)) {
                return false;
            }
            left++;
            right--;
        }
        
        return true;
    }

    public static void main(String[] args) {
        String str = "Dot saw I was Tod";
        boolean isPalindrome = isPalindrome(str);

        System.out.println(str + " is palindrome: " + isPalindrome);
    }
}



