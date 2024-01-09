## what does "Big O of n" mean in practice?
Answer: 

It means that the time it takes to run the algorithm is proportional to the size of the input

## Will an O(n) algorithm always outperform an O(n*n) algorithm?
Answer: 

No, it depends on the size of the input. For example, if the input is small, then O(n * n) may outperform O(n) because O(n * n) may have a smaller constant factor than O(n) in practice. 

(e.g. O(n*n) may be 0.1 seconds while O(n) may be 0.2 seconds) and the difference is negligible.
Other factors may also affect the performance of an algorithm, such as the hardware, the programming language, code optimization, will also affect the performance.

--------------

Note: 
- Constant factors mean the factors that are not related to the size of the input. 
- For example, if an algorithm takes 0.1 seconds to run, then 0.1 is the constant factor. 
- Another example is 2n, where 2 is the constant factor.

