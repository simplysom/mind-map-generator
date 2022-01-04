# from nltk.stem.wordnet import WordNetLemmatizer
import spacy

SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
OBJECTS = ["dobj", "dative", "attr", "oprd"]


def getSubsFromConjunctions(subs):
    moreSubs = []
    for sub in subs:
        # rights is a generator
        rights = list(sub.rights)
        rightDeps = {tok.lower_ for tok in rights}
        if "and" in rightDeps:
            moreSubs.extend([tok for tok in rights if tok.dep_ in SUBJECTS or tok.pos_ == "NOUN"])
            if len(moreSubs) > 0:
                moreSubs.extend(getSubsFromConjunctions(moreSubs))
    return moreSubs

def getObjsFromConjunctions(objs):
    moreObjs = []
    for obj in objs:
        # rights is a generator
        rights = list(obj.rights)
        rightDeps = {tok.lower_ for tok in rights}
        if "and" in rightDeps:
            moreObjs.extend([tok for tok in rights if tok.dep_ in OBJECTS or tok.pos_ == "NOUN"])
            if len(moreObjs) > 0:
                moreObjs.extend(getObjsFromConjunctions(moreObjs))
    return moreObjs

def getVerbsFromConjunctions(verbs):
    moreVerbs = []
    for verb in verbs:
        rightDeps = {tok.lower_ for tok in verb.rights}
        if "and" in rightDeps:
            moreVerbs.extend([tok for tok in verb.rights if tok.pos_ == "VERB"])
            if len(moreVerbs) > 0:
                moreVerbs.extend(getVerbsFromConjunctions(moreVerbs))
    return moreVerbs

def findSubs(tok):
    head = tok.head
    while head.pos_ != "VERB" and head.pos_ != "NOUN" and head.head != head:
        head = head.head
    if head.pos_ == "VERB":
        subs = [tok for tok in head.lefts if tok.dep_ == "SUB"]
        if len(subs) > 0:
            verbNegated = isNegated(head)
            subs.extend(getSubsFromConjunctions(subs))
            return subs, verbNegated
        elif head.head != head:
            return findSubs(head)
    elif head.pos_ == "NOUN":
        return [head], isNegated(tok)
    return [], False

def isNegated(tok):
    negations = {"no", "not", "n't", "never", "none"}
    for dep in list(tok.lefts) + list(tok.rights):
        if dep.lower_ in negations:
            return True
    return False

def findSVs(tokens):
    svs = []
    verbs = [tok for tok in tokens if tok.pos_ == "VERB"]
    for v in verbs:
        subs, verbNegated = getAllSubs(v)
        if len(subs) > 0:
            for sub in subs:
                svs.append((sub.orth_, "!" + v.orth_ if verbNegated else v.orth_))
    return svs

def getObjsFromPrepositions(deps):
    objs = []
    for dep in deps:
        if dep.pos_ == "ADP" and dep.dep_ == "prep":
            objs.extend([tok for tok in dep.rights if tok.dep_  in OBJECTS or (tok.pos_ == "PRON" and tok.lower_ == "me")])
    return objs

def getObjsFromAttrs(deps):
    for dep in deps:
        if dep.pos_ == "NOUN" and dep.dep_ == "attr":
            verbs = [tok for tok in dep.rights if tok.pos_ == "VERB"]
            if len(verbs) > 0:
                for v in verbs:
                    rights = list(v.rights)
                    objs = [tok for tok in rights if tok.dep_ in OBJECTS]
                    objs.extend(getObjsFromPrepositions(rights))
                    if len(objs) > 0:
                        return v, objs
    return None, None

def getObjFromXComp(deps):
    for dep in deps:
        if dep.pos_ == "VERB" and dep.dep_ == "xcomp":
            v = dep
            rights = list(v.rights)
            objs = [tok for tok in rights if tok.dep_ in OBJECTS]
            objs.extend(getObjsFromPrepositions(rights))
            if len(objs) > 0:
                return v, objs
    return None, None

def getAllSubs(v):
    verbNegated = isNegated(v)
    subs = [tok for tok in v.lefts if tok.dep_ in SUBJECTS and tok.pos_ != "DET"]
    if len(subs) > 0:
        subs.extend(getSubsFromConjunctions(subs))
    else:
        foundSubs, verbNegated = findSubs(v)
        subs.extend(foundSubs)
    return subs, verbNegated

def getAllObjs(v):
    # rights is a generator
    rights = list(v.rights)
    objs = [tok for tok in rights if tok.dep_ in OBJECTS]
    objs.extend(getObjsFromPrepositions(rights))

    #potentialNewVerb, potentialNewObjs = getObjsFromAttrs(rights)
    #if potentialNewVerb is not None and potentialNewObjs is not None and len(potentialNewObjs) > 0:
    #    objs.extend(potentialNewObjs)
    #    v = potentialNewVerb

    potentialNewVerb, potentialNewObjs = getObjFromXComp(rights)
    if potentialNewVerb is not None and potentialNewObjs is not None and len(potentialNewObjs) > 0:
        objs.extend(potentialNewObjs)
        v = potentialNewVerb
    if len(objs) > 0:
        objs.extend(getObjsFromConjunctions(objs))
    return v, objs

def findSVOs(tokens):
	svos=[]
	verbs = [tok for tok in tokens if tok.pos_ == "VERB" and tok.dep_ != "aux"]
	for v in verbs:
	    subs, verbNegated = getAllSubs(v)
	    # hopefully there are subs, if not, don't examine this verb any longer
	    if len(subs) > 0:
	        v, objs = getAllObjs(v)
	        for sub in subs:
	            for obj in objs:
	                objNegated = isNegated(obj)
	                svos.append((sub, "!" + v.lower_ if verbNegated or objNegated else v.lower_, obj))
	return svos

def getAbuserOntoVictimSVOs(tokens):
    maleAbuser = {'he', 'boyfriend', 'bf', 'father', 'dad', 'husband', 'brother', 'man'}
    femaleAbuser = {'she', 'girlfriend', 'gf', 'mother', 'mom', 'wife', 'sister', 'woman'}
    neutralAbuser = {'pastor', 'abuser', 'offender', 'ex', 'x', 'lover', 'church', 'they'}
    victim = {'me', 'sister', 'brother', 'child', 'kid', 'baby', 'friend', 'her', 'him', 'man', 'woman'}

    svos = findSVOs(tokens)
    wnl = WordNetLemmatizer()
    passed = []
    for s, v, o in svos:
        s = wnl.lemmatize(s)
        v = "!" + wnl.lemmatize(v[1:], 'v') if v[0] == "!" else wnl.lemmatize(v, 'v')
        o = "!" + wnl.lemmatize(o[1:]) if o[0] == "!" else wnl.lemmatize(o)
        if s in maleAbuser.union(femaleAbuser).union(neutralAbuser) and o in victim:
            passed.append((s, v, o))
    return passed

def printDeps(toks):
    for tok in toks:
        print(tok.orth_, tok.dep_, tok.pos_, tok.head.orth_, [t.orth_ for t in tok.lefts], [t.orth_ for t in tok.rights])

def testSVOs():
    nlp = spacy.load("en")

    tok = nlp("making $12 an hour? where am i going to go? i have no other financial assistance available and he certainly won't provide support.")
    svos = findSVOs(tok)
    printDeps(tok)
    assert set(svos) == {('i', '!have', 'assistance'), ('he', '!provide', 'support')}
    print(svos)

    tok = nlp("i don't have other assistance")
    svos = findSVOs(tok)
    printDeps(tok)
    assert set(svos) == {('i', '!have', 'assistance')}

    print("-----------------------------------------------")
    tok = nlp("They ate the pizza with anchovies.")
    svos = findSVOs(tok)
    printDeps(tok)
    print(svos)
    assert set(svos) == {('they', 'ate', 'pizza')}

    print("--------------------------------------------------")
    tok = nlp("I have no other financial assistance available and he certainly won't provide support.")
    svos = findSVOs(tok)
    printDeps(tok)
    print(svos)
    assert set(svos) == {('i', '!have', 'assistance'), ('he', '!provide', 'support')}

    print("--------------------------------------------------")
    tok = nlp("I have no other financial assistance available, and he certainly won't provide support.")
    svos = findSVOs(tok)
    printDeps(tok)
    print(svos)
    assert set(svos) == {('i', '!have', 'assistance'), ('he', '!provide', 'support')}

    print("--------------------------------------------------")
    tok = nlp("he did not kill me")
    svos = findSVOs(tok)
    printDeps(tok)
    print(svos)
    assert set(svos) == {('he', '!kill', 'me')}

    #print("--------------------------------------------------")
    #tok = nlp("he is an evil man that hurt my child and sister")
    #svos = findSVOs(tok)
    #printDeps(tok)
    #print(svos)
    #assert set(svos) == {('he', 'hurt', 'child'), ('he', 'hurt', 'sister'), ('man', 'hurt', 'child'), ('man', 'hurt', 'sister')}

    print("--------------------------------------------------")
    tok = nlp("he told me i would die alone with nothing but my career someday")
    svos = findSVOs(tok)
    printDeps(tok)
    print(svos)
    assert set(svos) == {('he', 'told', 'me')}

    print("--------------------------------------------------")
    tok = nlp("I wanted to kill him with a hammer.")
    svos = findSVOs(tok)
    printDeps(tok)
    print(svos)
    assert set(svos) == {('i', 'kill', 'him')}

    print("--------------------------------------------------")
    tok = nlp("because he hit me and also made me so angry i wanted to kill him with a hammer.")
    svos = findSVOs(tok)
    printDeps(tok)
    print(svos)
    assert set(svos) == {('he', 'hit', 'me'), ('i', 'kill', 'him')}

    print("--------------------------------------------------")
    tok = nlp("he and his brother shot me")
    svos = findSVOs(tok)
    printDeps(tok)
    print(svos)
    assert set(svos) == {('he', 'shot', 'me'), ('brother', 'shot', 'me')}

    print("--------------------------------------------------")
    tok = nlp("he and his brother shot me and my sister")
    svos = findSVOs(tok)
    printDeps(tok)
    print(svos)
    assert set(svos) == {('he', 'shot', 'me'), ('he', 'shot', 'sister'), ('brother', 'shot', 'me'), ('brother', 'shot', 'sister')}

    print("--------------------------------------------------")
    tok = nlp("the annoying person that was my boyfriend hit me")
    svos = findSVOs(tok)
    printDeps(tok)
    print(svos)
    assert set(svos) == {('person', 'was', 'boyfriend'), ('person', 'hit', 'me')}

    print("--------------------------------------------------")
    tok = nlp("the boy raced the girl who had a hat that had spots.")
    svos = findSVOs(tok)
    printDeps(tok)
    print(svos)
    assert set(svos) == {('boy', 'raced', 'girl'), ('who', 'had', 'hat'), ('hat', 'had', 'spots')}

    print("--------------------------------------------------")
    tok = nlp("he spit on me")
    svos = findSVOs(tok)
    printDeps(tok)
    print(svos)
    assert set(svos) == {('he', 'spit', 'me')}

    print("--------------------------------------------------")
    tok = nlp("he didn't spit on me")
    svos = findSVOs(tok)
    printDeps(tok)
    print(svos)
    assert set(svos) == {('he', '!spit', 'me')}

    print("--------------------------------------------------")
    tok = nlp("the boy raced the girl who had a hat that didn't have spots.")
    svos = findSVOs(tok)
    printDeps(tok)
    print(svos)
    assert set(svos) == {('boy', 'raced', 'girl'), ('who', 'had', 'hat'), ('hat', '!have', 'spots')}

    print("--------------------------------------------------")
    tok = nlp("he is a nice man that didn't hurt my child and sister")
    svos = findSVOs(tok)
    printDeps(tok)
    print(svos)
    assert set(svos) == {('he', 'is', 'man'), ('man', '!hurt', 'child'), ('man', '!hurt', 'sister')}

    print("--------------------------------------------------")
    tok = nlp("he didn't spit on me and my child")
    svos = findSVOs(tok)
    printDeps(tok)
    print(svos)
    assert set(svos) == {('he', '!spit', 'me'), ('he', '!spit', 'child')}

    print("--------------------------------------------------")
    tok = nlp("he beat and hurt me")
    svos = findSVOs(tok)
    printDeps(tok)
    print(svos)
    # tok = nlp("he beat and hurt me")

def main():
    # testSVOs()
    print("--------------------------------------------------")
    nlp=spacy.load("en")
    tok = nlp("""In botany, a tree is a perennial plant with an elongated stem, or trunk, supporting branches and leaves in most species. In some usages, the definition of a tree may be narrower, including only woody plants with secondary growth, plants that are usable as lumber or plants above a specified height. Trees are not a taxonomic group but include a variety of plant species that have independently evolved a woody trunk and branches as a way to tower above other plants to compete for sunlight. Trees tend to be long-lived, some reaching several thousand years old. In wider definitions, the taller palms, tree ferns, bananas, and bamboos are also trees. Trees have been in existence for 370 million years. It is estimated that there are just over 3 trillion mature trees in the world.[1]

A tree typically has many secondary branches supported clear of the ground by the trunk. This trunk typically contains woody tissue for strength, and vascular tissue to carry materials from one part of the tree to another. For most trees it is surrounded by a layer of bark which serves as a protective barrier. Below the ground, the roots branch and spread out widely; they serve to anchor the tree and extract moisture and nutrients from the soil. Above ground, the branches divide into smaller branches and shoots. The shoots typically bear leaves, which capture light energy and convert it into sugars by photosynthesis, providing the food for the tree's growth and development.

Trees usually reproduce using seeds. Flowers and fruit may be present, but some trees, such as conifers, instead have pollen cones and seed cones. Palms, bananas, and bamboos also produce seeds, but tree ferns produce spores instead.""")
    svos = findSVOs(tok)
    # printDeps(tok)
    print(svos)

if __name__ == "__main__":
    main()
