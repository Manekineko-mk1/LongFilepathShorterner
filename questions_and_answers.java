public class questions_and_answers {
    // 1. When do you overload a method in Java and when do you override it?
    // Answer: 
    //  - We should use overloading when we want to add more to the behavior of a method
    //  - We should use overriding when we want to change the behavior of a method

    // 2. When will you override equals and hashCode?
    // Answer: When we want to compare two objects of a class for equality, we override the equals() and hashCode() methods.

    // 3. What is the Collection class in Java?
    // Answer: The Collection in Java is a framework that provides an architecture to store and manipulate the group of objects.
    //  - Common methods of Collection interface: add(), remove(), removeAll(), retainAll(), contains(), 
    //      containsAll(), size(), toArray(), clear(), isEmpty(), iterator(), spliterator(), stream(), parallelStream()

    // 4. What is the difference between ArrayList and LinkedList?
    // Answer: 
    //  - 1. ArrayList internally uses a dynamic array to store the elements. LinkedList internally uses a doubly linked list to store the elements.
    //  - 2. Manipulation with ArrayList is slow because it internally uses an array. 
    //       If any element is removed from the array, all the bits are shifted in memory. 
    //       Manipulation with LinkedList is faster than ArrayList because it uses a doubly linked list, so no bit shifting is required in memory.
    //  - 3. An ArrayList class can act as a list only because it implements List only.
    //       LinkedList class can act as a list and queue both because it implements List and Deque interfaces.
    //  - 4. ArrayList is better for storing and accessing data. LinkedList is better for manipulating data.

    // 5. What is the difference between a List, Set, and Map?
    // Answer:
    //  - List: An ordered collection (also known as a sequence). The user of this interface has precise control over where in the list each element is inserted.
    //  - Set: A collection that contains no duplicate elements.
    //  - Map: An object that maps keys to values. A map cannot contain duplicate keys; each key can map to at most one value.
    
    // 6. What is the difference between a HashMap and a Hashtable?
    // Answer:
    //  - HashMap is non-synchronized. It is not-thread safe and can’t be shared between many threads without proper synchronization code whereas Hashtable is synchronized.
    //  - HashMap allows one null key and multiple null values whereas Hashtable doesn’t allow any null key or value.
    //  - HashMap is generally preferred over HashTable if thread synchronization is not needed

    // 7. What is the difference between a HashMap and a HashSet?
    // Answer:
    //  - HashMap is an implementation of Map interface while HashSet is an implementation of Set interface.
    //  - HashMap stores key-value pairs while HashSet only stores objects.
    //  - HashMap is implemented by using an array of the list. When we call put() method by passing key-value pair,
    //      it uses hashCode() and equals() methods to find out the index for storing the value whereas in HashSet,
    //      we use add() method to store the objects. It internally uses hashCode() and equals() methods to store the objects.

    // 8. Is Java “pass-by-reference” or “pass-by-value”?
    // Answer:
    //  - Pass-by-value: When we pass primitive data types (int, float, double, etc.) as arguments to a method, it is passed by value.
    //  - Pass-by-reference: When we pass objects of a class as arguments to a method, it is passed by reference.
    //  - In Java, all the arguments are passed by value. However, when we pass the object of a class as an argument, it is passed as the reference of that object.

    // 9. Explain the difference between a class and an object.
    // Answer:
    //  - Class: A class is a blueprint or prototype from which objects are created.
    //  - Object: An object is an instance of a class. A class is a template, blueprint, or contract that defines what an object’s data fields and methods will be.

    // 10. What is the difference between an abstract class and an interface?
    // Answer:
    //  - Abstract class: An abstract class can have abstract and non-abstract methods. It needs to be extended and its method implemented.
    //  - Interface: An interface can have only abstract methods. The class implementing the interface needs to implement all the methods of the interface.
    //  - An abstract class can have protected and abstract methods whereas an interface can have only public abstract methods.
    //  - A class can implement multiple interfaces but it can extend only one abstract class.
    //  - An abstract class can have static, final, static final variables with any access specifier but an interface can have only static final variables with public access specifier.

    // 11. Explain OOP to a non-technical person.
    // Answer:
    //  - OOP is a programming paradigm based on the concept of “objects”. 
    //  - You can think of an object as a model of the concepts, processes, or things in the real world that are meaningful to your application.
    //  - An object contains data and behavior. The data in an object represents the state of your application, 
    //      and the behavior represents the actions that can be performed by your application.
    //  - For example, a car is an object which has certain properties such as color, number of doors, and the like.
    //      It also has certain methods to represent car behaviour such as accelerate, brake, and so on.

    // 12. What are the four principles of OOP?
    // Answer:
    //  - Encapsulation: The process of combining data and functions into a single unit called class is known as encapsulation.
    //  - Abstraction: The process of hiding the internal details and describing things in simple terms is known as abstraction.
    //  - Inheritance: The process by which one class acquires the properties of another class is called inheritance.
    //  - Polymorphism: The feature that allows one interface to be used for general class actions is known as polymorphism.

    // 13. Explain the four principles of OOP to a non-technical person.
    // Answer:
    //  - Encapsulation: Encapsulation is like enclosing something in a capsule.
    //      The purpose of encapsulation is to protect the data from the outside world.
    //      For example, the save button on a word processor encapsulates the code that actually saves a file.
    //  - Abstraction: Abstraction is like a summary. It is a simplified view of an object by hiding unnecessary details.
    //      For example, abstraction is used in a car. You don’t need to know how the engine works to drive a car.
    //  - Inheritance: Inheritance is like a child inheriting genes from his parents.
    //      It is a mechanism where a new class acquires the properties of the existing class.
    //      For example, a child inherits the traits of his/her parents.
    //  - Polymorphism: Polymorphism is like a person having more than one form.
    //      It is a feature that allows one interface to be used for general class actions.
    //      For example, a person at the same time can have different characteristics.
    






    // Check if a given number is prime or not
    public static boolean isPrime(int num) {
        if (num <= 1) {
            return false;
        }

        // Check from 2 to n-1
        for (int i = 2; i < num; i++) {
            if (num % i == 0) {
                // Found a divisor, not a prime number
                return false;
            }
        }

        return true;
    }
    
}
