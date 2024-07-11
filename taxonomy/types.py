from typing import Generic, List, Optional, TypeVar, TypedDict


class Leaf(TypedDict):
    overview: str
    specifics: List[str]
    parent: 'Node'

T = TypeVar('T')

class Node(Generic[T]):
    children: List[T]
    topic: Optional[str]
    payload: Optional[Leaf]
    def __init__(self, children: List[T], topic: Optional[str], payload: Optional['Leaf']):
        self.children = children
        self.topic = topic
        self.payload = payload
    
    def toJson(self):
        if (self.children):
            childrenJson = [child.toJson() for child in self.children]
        else:
            childrenJson = []
        return {
            "topic": self.topic,
            "payload": self.payload,
            "children": childrenJson
        }

    def nodeFromJson(json):
        childrenJson = json["children"]
        childrenNodes = [Node.nodeFromJson(c) for c in childrenJson]
        topic = json["topic"]
        payload = json["payload"]
        return Node(childrenNodes, topic=topic, payload=payload)