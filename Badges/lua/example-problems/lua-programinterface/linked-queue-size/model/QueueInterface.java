/**
   An interface for the ADT queue.
   
   @author Frank M. Carrano
   @version 3.0
*/
public interface QueueInterface<T>
{
  /*  Adds a new entry to the back of this queue.
      @param newEntry  an object to be added */
  public void enqueue(T newEntry);
  
  /*  Removes and returns the entry at the front of this queue.
      @return either the object at the front of the queue or, if the
              queue is empty before the operation, null */
  public T dequeue();
  
  /*  Retrieves the entry at the front of this queue.
      @return either the object at the front of the queue or, if the
              queue is empty, null */
  public T getFront();
  
  /*  Detects whether this queue is empty.
      @return true if the queue is empty, or false otherwise */
  public boolean isEmpty();
  
  /*  Removes all entries from this queue. */
  public T size(T newEntry);
  
  // Merges two queues together
  
  public void clear();

 /* Add all items in queue2 to the end of the queue on which the method is applied.
 * The firstNode of the first chain will be the firstNode of the result
 * The lastNode of the second chain will be the last node of the result
 */
   public QueueInterface<T>  splice(QueueInterface<T> queue2);
   
} // end QueueInterface