from __future__ import annotations
from openpyxl.styles import Font
from math import floor
from random import randint
import logging
import logging.config
import os
import json
import openpyxl
import logging
import logging.config
import cProfile #Trying this method for profiling
import pstats #we need this to save the profiling results


logging.config.fileConfig(fname='myeditorlog.conf', disable_existing_loggers = False)

# Get the logger specified in the file
logger = logging.getLogger(__name__)

###########################################BplustreeStart##############################################
class Node:
    """
    Base node object.

    Attributes:
        order (int): The maximum number of keys each node can hold (branching factor).
    """
    uidCounter = 0

    def __init__(self, order):
        self.order = order
        self.parent: Node = None
        self.keys = []
        self.values = []

        #  This is for Debugging purposes only!
        Node.uidCounter += 1
        self.uid = self.uidCounter


    def split(self) -> Node:  # Split a full Node to two new ones.
        left = Node(self.order)
        right = Node(self.order)
        mid = int(self.order // 2)

        left.parent = right.parent = self

        left.keys = self.keys[:mid]
        left.values = self.values[:mid + 1]

        right.keys = self.keys[mid + 1:]
        right.values = self.values[mid + 1:]

        self.values = [left, right]  # Setup the pointers to child nodes.

        self.keys = [self.keys[mid]]  # Hold the first element from the right subtree.

        # Setup correct parent for each child node.
        for child in left.values:
            if isinstance(child, Node):
                child.parent = left

        for child in right.values:
            if isinstance(child, Node):
                child.parent = right

        return self  # Return the 'top node'

    def getSize(self) -> int:
        return len(self.keys)

    def isEmpty(self) -> bool:
        return len(self.keys) == 0

    def isFull(self) -> bool:
        return len(self.keys) == self.order - 1

    def isNearlyUnderflow(self) -> bool:  # Used to check on keys, not data!
        return len(self.keys) <= floor(self.order / 2)

    def isUnderflow(self) -> bool:  # Used to check on keys, not data!
        return len(self.keys) <= floor(self.order / 2) - 1

    def isRoot(self) -> bool:
        return self.parent is None


class LeafNode(Node):
    def __init__(self, order):
        super().__init__(order)

        self.prevLeaf: LeafNode = None
        self.nextLeaf: LeafNode = None

    # TODO: Implement an improved version
    def add(self, key, value):
        if not self.keys:  # Insert key if it doesn't exist
            self.keys.append(key)
            self.values.append([value])
            return

        for i, item in enumerate(self.keys):  # Otherwise, search key and append value.
            if key == item:  # Key found => Append Value
                self.values[i].append(value)  # Remember, this is a list of data. Not nodes!
                break

            elif key < item:  # Key not found && key < item => Add key before item.
                self.keys = self.keys[:i] + [key] + self.keys[i:]
                self.values = self.values[:i] + [[value]] + self.values[i:]
                break

            elif i + 1 == len(self.keys):  # Key not found here. Append it after.
                self.keys.append(key)
                self.values.append([value])
                break

    def split(self) -> Node:  # Split a full leaf node. (Different method used than before!)
        top = Node(self.order)
        right = LeafNode(self.order)
        mid = int(self.order // 2)

        self.parent = right.parent = top

        right.keys = self.keys[mid:]
        right.values = self.values[mid:]
        right.prevLeaf = self
        right.nextLeaf = self.nextLeaf

        top.keys = [right.keys[0]]
        top.values = [self, right]  # Setup the pointers to child nodes.

        self.keys = self.keys[:mid]
        self.values = self.values[:mid]
        self.nextLeaf = right  # Setup pointer to next leaf

        return top  # Return the 'top node'


class BPlusTree(object):
    def __init__(self, order=5):
        self.root: Node = LeafNode(order)  # First node must be leaf (to store data).
        self.order: int = order

    @staticmethod
    def _find(node: Node, key):
        for i, item in enumerate(node.keys):
            if key < item:
                return node.values[i], i
            elif i + 1 == len(node.keys):
                return node.values[i + 1], i + 1  # return right-most node/pointer.

    @staticmethod
    def _mergeUp(parent: Node, child: Node, index):
        parent.values.pop(index)
        pivot = child.keys[0]

        for c in child.values:
            if isinstance(c, Node):
                c.parent = parent

        for i, item in enumerate(parent.keys):
            if pivot < item:
                parent.keys = parent.keys[:i] + [pivot] + parent.keys[i:]
                parent.values = parent.values[:i] + child.values + parent.values[i:]
                break

            elif i + 1 == len(parent.keys):
                parent.keys += [pivot]
                parent.values += child.values
                break

    def insert(self, key, value):
        node = self.root

        while not isinstance(node, LeafNode):  # While we are in internal nodes... search for leafs.
            node, index = self._find(node, key)

        # Node is now guaranteed a LeafNode!
        node.add(key, value)

        while len(node.keys) == node.order:  # 1 over full
            if not node.isRoot():
                parent = node.parent
                node = node.split()  # Split & Set node as the 'top' node.
                jnk, index = self._find(parent, node.keys[0])
                self._mergeUp(parent, node, index)
                node = parent
            else:
                node = node.split()  # Split & Set node as the 'top' node.
                self.root = node  # Re-assign (first split must change the root!)

    def retrieve(self, key):
        node = self.root

        while not isinstance(node, LeafNode):
            node, index = self._find(node, key)

        for i, item in enumerate(node.keys):
            if key == item:
                return node.values[i]

        return None

    def delete(self, key):
        node = self.root

        while not isinstance(node, LeafNode):
            node, parentIndex = self._find(node, key)

        if key not in node.keys:
            return False

        index = node.keys.index(key)
        node.values[index].pop()  # Remove the last inserted data.

        if len(node.values[index]) == 0:
            node.values.pop(index)  # Remove the list element.
            node.keys.pop(index)

            while node.isUnderflow() and not node.isRoot():
                # Borrow attempt:
                prevSibling = BPlusTree.getPrevSibling(node)
                nextSibling = BPlusTree.getNextSibling(node)
                jnk, parentIndex = self._find(node.parent, key)

                if prevSibling and not prevSibling.isNearlyUnderflow():
                    self._borrowLeft(node, prevSibling, parentIndex)
                elif nextSibling and not nextSibling.isNearlyUnderflow():
                    self._borrowRight(node, nextSibling, parentIndex)
                elif prevSibling and prevSibling.isNearlyUnderflow():
                    self._mergeOnDelete(prevSibling, node)
                elif nextSibling and nextSibling.isNearlyUnderflow():
                    self._mergeOnDelete(node, nextSibling)

                node = node.parent

            if node.isRoot() and not isinstance(node, LeafNode) and len(node.values) == 1:
                self.root = node.values[0]
                self.root.parent = None

    @staticmethod
    def _borrowLeft(node: Node, sibling: Node, parentIndex):
        if isinstance(node, LeafNode):  # Leaf Redistribution
            key = sibling.keys.pop(-1)
            data = sibling.values.pop(-1)
            node.keys.insert(0, key)
            node.values.insert(0, data)

            node.parent.keys[parentIndex - 1] = key  # Update Parent (-1 is important!)
        else:  # Inner Node Redistribution (Push-Through)
            parent_key = node.parent.keys.pop(-1)
            sibling_key = sibling.keys.pop(-1)
            data: Node = sibling.values.pop(-1)
            data.parent = node

            node.parent.keys.insert(0, sibling_key)
            node.keys.insert(0, parent_key)
            node.values.insert(0, data)

    @staticmethod
    def _borrowRight(node: LeafNode, sibling: LeafNode, parentIndex):
        if isinstance(node, LeafNode):  # Leaf Redistribution
            key = sibling.keys.pop(0)
            data = sibling.values.pop(0)
            node.keys.append(key)
            node.values.append(data)
            node.parent.keys[parentIndex] = sibling.keys[0]  # Update Parent
        else:  # Inner Node Redistribution (Push-Through)
            parent_key = node.parent.keys.pop(0)
            sibling_key = sibling.keys.pop(0)
            data: Node = sibling.values.pop(0)
            data.parent = node

            node.parent.keys.append(sibling_key)
            node.keys.append(parent_key)
            node.values.append(data)

    @staticmethod
    def _mergeOnDelete(l_node: Node, r_node: Node):
        parent = l_node.parent

        jnk, index = BPlusTree._find(parent, l_node.keys[0])  # Reset pointer to child
        parent_key = parent.keys.pop(index)
        parent.values.pop(index)
        parent.values[index] = l_node

        if isinstance(l_node, LeafNode) and isinstance(r_node, LeafNode):
            l_node.nextLeaf = r_node.nextLeaf  # Change next leaf pointer
        else:
            l_node.keys.append(parent_key)  # TODO Verify this
            for r_node_child in r_node.values:
                r_node_child.parent = l_node

        l_node.keys += r_node.keys
        l_node.values += r_node.values

    @staticmethod
    def getPrevSibling(node: Node) -> Node:
        if node.isRoot() or not node.keys:
            return None
        jnk, index = BPlusTree._find(node.parent, node.keys[0])
        return node.parent.values[index - 1] if index - 1 >= 0 else None

    @staticmethod
    def getNextSibling(node: Node) -> Node:
        if node.isRoot() or not node.keys:
            return None
        jnk, index = BPlusTree._find(node.parent, node.keys[0])

        return node.parent.values[index + 1] if index + 1 < len(node.parent.values) else None

    def printTree(self):
        if self.root.isEmpty():
            print('The bpt+ Tree is empty!')
            return
        queue = [self.root, 0]  # Node, Height... Not systematic but it works

        while len(queue) > 0:
            node = queue.pop(0)
            height = queue.pop(0)

            if not isinstance(node, LeafNode):
                queue += self.intersperse(node.values, height + 1)
            print('Level ' + str(height), '|'.join(map(str, node.keys)), ' -->\t current -> ', node.uid,
                  '\t parent -> ',
                  node.parent.uid if node.parent else None)

    def getLeftmostLeaf(self):
        if not self.root:
            return None

        node = self.root
        while not isinstance(node, LeafNode):
            node = node.values[0]

        return node

    def getRightmostLeaf(self):
        if not self.root:
            return None

        node = self.root
        while not isinstance(node, LeafNode):
            node = node.values[-1]

    def showAllData(self):
        node = self.getLeftmostLeaf()
        if not node:
            return None

        while node:
            for node_data in node.values:
                print('[{}]'.format(', '.join(map(str, node_data))), end=' -> ')

            node = node.nextLeaf
        print('Last node')

    def showAllDataReverse(self):
        node = self.getRightmostLeaf()
        if not node:
            return None

        while node:
            for node_data in reversed(node.values):
                print('[{}]'.format(', '.join(map(str, node_data))), end=' <- ')

            node = node.prevLeaf
        print()

    @staticmethod
    def intersperse(lst, item):
        result = [item] * (len(lst) * 2)
        result[0::2] = lst
        return result

#############################################BplustreeEnd##############################################

#################################################MainStart#############################################

class read_files:
    @staticmethod
    def is_utf8(line):
        try:
            line.encode('utf-8')
            return True
        except UnicodeDecodeError:
            return False

    @staticmethod
    def read_pairs_from_file(file_name, bpt_instance):
        """
        Reads pairs from a file and stores them in the keys dictionary.
        """
        keys = {}
        already_inserted = set()
        bplus_set = set()
        try:
            if not isinstance(file_name, str):
                raise ValueError("file_name must be a string.")
            if not os.path.isfile(file_name):
                raise ValueError(f"File {file_name} does not exist.")
        except Exception as e:
            print(f"An error occurred: {e}")

        try:
            with open(file_name, 'r', encoding = "latin1") as file:
                for line in file:
                    # '\n' is a newline,'\t' is a tab,'\v' is a vertical tab,'\b' is a backspace,'\0' is a null character.
                    if line[0] in ['#', '%', '^', '_', '!', '@', '$', '*', ' ' , '\n', '\t', '\v', '\b', '\0']:
                        continue
                    else:
                        elements = line.split()
                        if len(elements) >= 2:
                            if ":" in line:
                                document_id = elements[0]  # Extract document ID
                                term = set()

                                for element in elements[1:]:
                                    if ':' in element:
                                        term.add(element.split(':')[0])  # Add only the term before colon to the set

                                if document_id in already_inserted:
                                    keys[document_id].update(term)
                                    if document_id in bplus_set:
                                        bpt_instance.retrieve(document_id).add(term)
                                    else:
                                        bpt_instance.insert(document_id, term)
                                else:
                                    already_inserted.add(document_id)
                                    keys[document_id] = term
                                    if document_id in bplus_set:
                                        bpt_instance.retrieve(document_id).add(term)
                                    else:
                                        bpt_instance.insert(document_id, term)
                            else:
                                key = elements[0]
                                value = elements[1]

                                if key in already_inserted:
                                    if value in bplus_set:
                                        keys[key].add(value)
                                        bpt_instance.retrieve(key).add(value)
                                    else:
                                        keys[key].add(value)
                                        bpt_instance.insert(value, {key})
                                else:
                                    already_inserted.add(key)
                                    keys[key] = {value}
                                    if value in bplus_set:
                                        bpt_instance.retrieve(value).add(key)
                                    else:
                                        bpt_instance.insert(value, {key})
        except IOError:
            print(f"Could not read file: {file_name}")

        print("Files have been stored")
        return keys

class write_files:
    def __init__(self, file_name, data_to_write, type_of_file):
        try:
            if not isinstance(file_name, str):
                raise ValueError("The file name must be a string.")
            if not isinstance(data_to_write, dict):
                raise ValueError("data_to_write must be a dictionary.")
            if not isinstance(type_of_file, str):
                raise ValueError("The file type must be a string.")
            if type_of_file not in ("json", "xlsx"):
                raise ValueError("The file type  must be either json or xlsx.")

            self.file_name = file_name
            self.data_to_write = data_to_write
            self.type_of_file = type_of_file
        except Exception as e:
            print(f"An error occurred: {e}")
            return

    def write_to_file(self):
            try:
                if self.type_of_file is not  None or self.file_name is not None:
                    user_file =  f"{self.file_name}.{self.type_of_file}"
                    with open(user_file, 'w') as file:
                        if self.type_of_file == "json":
                            json_data = []
                            for stem, categories in self.data_to_write.items():
                                for category, jaccard_index in categories.items():
                                    json_data.append({
                                        'stem': stem,
                                        'category': category,
                                        'jaccardIndex': jaccard_index
                                })
                            json.dump(json_data, file)

                        else:
                            wb = openpyxl.Workbook()
                            ws = wb.active
                            ws.title = "Jaccard Index"
                            ws.append(["Stem", "Category", "Jaccard Index"])
                            for stem, categories in self.data_to_write.items():
                                for category, jaccard_index in categories.items():
                                    ws.append([stem, category, jaccard_index])
                            wb.save(user_file)
            except IOError:
                print(f"Could not write to file: {self.file_name}")
                return

class jaccard_index:
    def __init__(self, category, term, stem):
        self.category = category
        self.term = term
        self.stem = stem
        self.jaccard_index = {}

    def calculate_jaccard_index(self):
        """
        Calculate the jaccard index for each stem and category
        """
        for stem_key, term_value in self.stem.items():
            self.jaccard_index[stem_key] = {}
            term_docs = set(self.get_term_docs(term_value))
            category_key = None
            for category_key, category_docs in self.category.items():
                category_docs_set = set(category_docs)
                intersection = len(term_docs & category_docs_set)
                union = len(term_docs | category_docs)
                self.jaccard_index[stem_key][category_key] = intersection / union
        return self.jaccard_index

    def get_term_docs(self, term_value):

       ##This is a method used to find documents which match the terms we want (term_value).
        term_docs = []
        term_value_set = set(term_value)

        for doc_id, terms in self.term.items():
            for term_list in terms:
                term_list_set = {term_list}
                if term_value_set & term_list_set:
                  term_docs.append(doc_id)
                 # break
        return set(term_docs) # remove duplicates

    def get_most_relevant_stems_for_category(self, category, k):
        """
        Get the top k stems for the given category
        """
        # Create a dictionary for the category
        category_jaccard_index = {}

        # Iterate over the jaccard_index dictionary
        for stem, categories in self.jaccard_index.items():
            # If the category exists in the inner dictionary, add it to the category_jaccard_index dictionary
            if category in categories:
                category_jaccard_index[stem] = categories[category]

        # If the category_jaccard_index dictionary is empty, the category was not found
        if not category_jaccard_index:
            print(f"Category {category} not found in jaccard_index.")
            return []

        # Sort the stems by their jaccard index in descending order
        sorted_stems = sorted(category_jaccard_index.items(), key=lambda item: item[1], reverse = True)

        # Get the top k stems
        top_k_stems = [stem for stem, _ in sorted_stems[:k]]

        return top_k_stems

    def get_most_relevant_categories_for_stem(self, stem, k):
        """
        Get the top k categories for the given stem
        """
        # Check if the stem exists in the jaccard_index
        if stem not in self.jaccard_index:
            print(f"Stem {stem} not found in jaccard_index.")
            return []

        # Get the jaccard index for the stem
        stem_jaccard_index = self.jaccard_index[stem]

        # Sort the categories by their jaccard index in descending order
        sorted_categories = sorted(stem_jaccard_index.items(), key = lambda item: item[1], reverse=True)

        # Get the top k categories
        top_k_categories = [category for category, _ in sorted_categories[:k]]

        return top_k_categories

class MainConsole:
    @staticmethod
    def main():
        print("Welcome to our application!")

        file_to_read_categories = "/content/rcv1-v2.topics.qrels.txt"
        file_to_read_term = "/content/lyrl2004_vectors_train.dat.txt"
        file_to_read_stems = "/content/stem.termid.idf.map.txt"

        order_of_tree = 10
        bpt_categories = BPlusTree(order_of_tree)
        bpt__term = BPlusTree(order_of_tree)
        bpt_stems = BPlusTree(order_of_tree)

        returned_data_categories = read_files.read_pairs_from_file(file_to_read_categories, bpt_categories) # Calling the method and storing the return value
        returned_data_term = read_files.read_pairs_from_file(file_to_read_term, bpt__term)
        returned_data_stems = read_files.read_pairs_from_file(file_to_read_stems, bpt_stems)

        #Profiling specific sections
        profile = cProfile.Profile()
        profile.enable()

        jaccard_instance =jaccard_index(returned_data_categories, returned_data_term, returned_data_stems)
        jaccard_index_value = jaccard_instance.calculate_jaccard_index()
        print("Jaccard Index has been calculated")

        profile.disable()
        print("\nThose are the results of profiling in Jaccard Index calculation method: \n")
        profile.print_stats()

if __name__ == "__main__":
    MainConsole.main()
#################################################MainEnd#############################################