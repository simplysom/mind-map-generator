# Mind-map-generator

## Motivation
Most of the information that we deal with in our day to day lives is in the form of huge stacks of
papers or documents. Perusing through these documents is very time consuming. Moreover,
manually constructing mind maps requires thorough reading and good understanding of the text
which is tedious.Therefore, automatically generating mind maps saves much time and
effort and helps in quick brainstorming which ultimately increases the productivity of the
workforce

## System Description
The user must enter the text or can use speech to text method
for the creation of mind map. This input text is then interpreted by the system modules and the
operations are performed to generate the output.
The user can save this generated output of the mind map directly to their system. The output
map can be directly saved as image on the user’s system

## Architecture
![alt text](https://github.com/simplysom/mind-map-generator/blob/main/mind-map-arch.png?raw=true)
## Challenges Faced
- Converting the input text into a corresponding mind map in minimal amount of time.
- Generating a multileveled mind map that gives a nodal representation of each and every
keyword.
- Effectively transcribing speech input to text in the presence of external noise

## Constraints
- The input text must be of size between 10 to 2500 words.
- The text input cannot be broken or highly unformatted.
- The input document must be only of standard file extension (.pdf, docx, txt).
- The web page used in input must be of w3 standards

## Future Scope
We aim to further improve the
project by making it multilingual i.e the system can make mindmaps not only from the text given in
English but also it can make mindmaps from textual data in other languages such as Hindi, French, etc.
The technology used for converting text in English to any other language is called neural machine
translation which is currently a primary area of research. Furthermore, we will try to add a pictorial
element to the graph by replacing all the nodes with the respective images they denote. Finally, we ain to
integrate with a cloud service such as Google Cloud Platform(GCP) where it can directly get hold of the
data stored in their cloud suite(google docs, google drive, etc)

#### Instructions
Run `python flask_server.py`.
You need to install the **PyAudio** module to enable the text to speech feature
