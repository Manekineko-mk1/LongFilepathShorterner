public class binary_search_tree {
    // binary search tree (BST) is a binary tree 
    // where the value of each node is larger or equal to the values in all the nodes in that node's left subtree 
    // and is smaller than the values in all the nodes in that node's right subtree.
    // for example: 
    //      5
    //     / \
    //    3   6
    //   / \
    //  2   4
    // / \
    //1   3
    // is a binary search tree (BST)
    // while this is not:
    //      5
    //     / \
    //    3   6
    //   / \
    //  2   4
    // / \
    //1   7
    // because 7 is larger than 5, which is the root node

    // implement binary search tree (BST)
    public static class Node {
        int val;
        Node left;
        Node right;

        public Node(int val) {
            this.val = val;
        }
    }

    // implement binary search tree methods for insertion
    public static Node insert(Node root, int val) {
        if (root == null) {
            return new Node(val);
        }

        if (val < root.val) {
            root.left = insert(root.left, val);
        } else if (val > root.val) {
            root.right = insert(root.right, val);
        }

        return root;
    }

    // implement binary search tree methods for deletion
    public static Node delete(Node root, int val) {
        if (root == null) {
            return null;
        }

        if (val < root.val) {
            root.left = delete(root.left, val);
        } else if (val > root.val) {
            root.right = delete(root.right, val);
        } else {
            // found the node to delete
            if (root.left == null) {
                return root.right;
            } else if (root.right == null) {
                return root.left;
            }

            // replace the value in the node with the smallest value from the right subtree
            root.val = findMin(root.right);

            // delete the node with the smallest value in the right subtree
            root.right = delete(root.right, root.val);
        }

        return root;
    }

    public static int findMin(Node node) {
        if (node.left == null) {
            return node.val;
        }
        return findMin(node.left);
    }

    // implement binary search tree methods for search
    public static boolean search(Node root, int val) {
        if (root == null) {
            return false;
        }

        if (val < root.val) {
            return search(root.left, val);
        } else if (val > root.val) {
            return search(root.right, val);
        } else {
            return true;
        }
    }

    // implement binary search tree methods for printing all leaves in a binary search tree
    public static void printLeaves(Node root) {
        if (root == null) {
            return;
        }

        if (root.left == null && root.right == null) {
            System.out.println(root.val);
        }

        printLeaves(root.left);
        printLeaves(root.right);
    }


    public static void main(String[] args) {
        // create a binary search tree
        Node root = null;

        // insert nodes
        root = insert(root, 5);
        root = insert(root, 3);

        // search for a node
        boolean found = search(root, 3);
        System.out.println("found: " + found);

        // delete a node
        root = delete(root, 3);
        found = search(root, 3);
        System.out.println("found: " + found);
    }
}
