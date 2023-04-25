# Assignment 3

### Areas in where my code would not function

- I think one area that can be clarified further is making sure that I am not adding the same conversation.
There is currently no way to verify duplicate information for conversations, so I can keep adding the same conversation
any time. My database would contain duplicate conversations that already exist.

- If there were multiple calls that were trying to write conversations, then my current codebase would not be able to handle that. I think it would slow down the response time or maybe create a timeout error.

- If I add a conversation with characters that do not exist in the database, that 
would present a problem. Right now, my code could add a conversation with a character that is
not in the database, but if I were to try to get the character from the character endpoints I would 
not be able to.

