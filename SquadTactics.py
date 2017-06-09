##-------------------------------------------------------------------------------
## Name:        Squad Tactics
##
## Author:      Walter Reis
##-------------------------------------------------------------------------------
##
## Base source: http://forrst.com/posts/A_algorithm_in_python-B4c

## Comments are in grey
#commented code is in green (debug to print to console)
## I have left the original authors comments, also

class Graph(object):
    """
    A simple undirected, weighted graph
    """
    def __init__(self):
        self.nodes = set()
        self.edges = {}
        self.distances = {}
        self.blocked_nodes= set()

    def set_blocked_nodes(self, node_set):
        self.blocked_nodes = node_set

    def add_blocked_node(self, value):
        self.blocked_nodes.add(value)

    def add_node(self, value):
        self.nodes.add(value)

    def add_edge(self, from_node, to_node, distance):
        self._add_edge(from_node, to_node, distance)
        self._add_edge(to_node, from_node, distance)

    def _add_edge(self, from_node, to_node, distance):
        self.edges.setdefault(from_node, [])
        self.edges[from_node].append(to_node)
        self.distances[(from_node, to_node)] = distance

## The A-Star core
def astar(graph, initial_node, goal_node, h):
    closed_set = set() # set of nodes already evaluated
    nodes = set() # set of tentative nodes to be evaluated
    nodes.add(initial_node)

    visited = {} # map of navigated nodes
    g_score = {initial_node: 0} # distance from start along optimal path
    h_score = {initial_node: h(initial_node, goal_node)} # heuristic estimate
    f_score = {initial_node: h_score[initial_node]} # estimated dist

    #print("astar values - " \
    #+ str(graph) + " " \
    #+ str(initial_node) + " " \
    #+ str(goal_node) + " " \
    #+ str(h))

    ## Loops through all the nodes
    while nodes:
        a = None
        for node in nodes:
            if a is None:
                a = node
            elif f_score[node] < f_score[a]:
                a = node
        nodes.remove(a)
        ## The goal node has been found, return the path
        if a == goal_node:
            #print("astar - reached goal")
            return visited

        closed_set.add(a)
        for b in graph.edges[a]:
            #print("in loop - " + str(b) + " " + str(a))
            ## Ignore the node if it has been considered,
            ## or if it is blocked
            if b in closed_set or a in g.blocked_nodes:
                continue
            #print("in loop - " + str(b) + " " + str(a))
            tentative_g_score = g_score[a] + graph.distances[(a, b)]

            flag = False
            if b not in nodes or tentative_g_score < g_score[b]:# or b not in g.blocked_nodes:
                #print(str(g.blocked_nodes))
                nodes.add(b)
                flag = True

            if flag:
                visited[b] = a

                g_score[b] = tentative_g_score
                h_score[b] = h(b, goal_node)
                f_score[b] = g_score[b] + h_score[b]

    ## If all else fails, return False
    return False

## Gets the shortest path
def shortest_path(graph, initial_node, goal_node, h):
    #print("shortest_path")
    print("shortest_path - initial_node: " \
    + str(initial_node) \
    + " goal_node: " \
    + str(goal_node))
    paths = astar(graph, initial_node, goal_node, h)
    route = [goal_node]

    ## Checks to see if the goal has been reached or if the the node is out of range
    while goal_node != initial_node \
    and goal_node[0] <= xSize \
    and goal_node[1] <= ySize \
    and goal_node[2] <= zSize:
        #print("shortest_path - goal_node type: " + str(type(goal_node)))
        #print("shortest_path - goal_node value: " + str(goal_node))
        #print("shortest_path - paths type: " + str(type(paths)))
        #print("shortest_path - paths: " + str((paths)))
        if(type(paths) == bool):
            print("Blocked path, try again!")
            break
        else:
            route.append(paths[goal_node])
            goal_node = paths[goal_node]
    ## Flips the route to start at the first node and end at the last
    route.reverse()
    #print("shortest_path - route: " + str(route))
    return route

## A Character class to control the path finding AI
class Character(object):

    ## Starts a character with default values if they are not provided at spawn time
    def __init__(self, \
    inName = "default name", \
    inMaxHealth = 100, \
    inPosition = (0,0,0), \
    inFaction = "enemy"):

        ## Check to see if the name is a string
        if(type(inName) is str):
            self.name = inName
        else:
            self.name = "INVALID NAME"

        ## Check to see if the maximum health is an integer
        if(type(inMaxHealth) is int):
            self.maxHealth = inMaxHealth
            self.health = self.maxHealth
        else:
            self.maxHealth = 100
            self.health = self.maxHealth

        ## Check to see if the position is a tuple
        if(type(inPosition) is tuple):
            self.position = inPosition
        else:
            self.position = (0,0,0)

        ## Check to see if the faction is a string
        if(type(inFaction) is str):
            self.faction = inFaction
        else:
            self.faction = "INVALID FACTION"

        ## Setting some defaults
        self.sldist = 0
        self.graph = Graph()
        self.closest_cover = (0,0,0)
        self.run_to_point = (0,0,0)
        self.number_of_close_allies = 0
        self.number_of_close_enemies = 0
        self.escape_route = dict()
        self.enemies = list()
        self.allies = list()
        self.squad_size = 1
        self.squad = self.allies

        #print("new character: " \
        #+ str(name) + " " \
        #+ str(health) + "/" \
        #+ str(maxHealth) + " " \
        #+ str(position) + " " \
        #+ str(faction))

    ## Moves the character to a point
    def move_to(self, new_pos):
        #print("Character.move_to - new pos " + str(new_pos))
        if type(new_pos) is tuple:
            print("Character.move_to - moving " + self.name + " from " + str(self.position) + " to "  + str(new_pos))
            self.position = new_pos

    ## Moves the character on a route, looping through the points
    def move(self, route):
        #print("Character.move - route " + str(route))
        index = 0
        while index < len(route):
            self.move_to(route[index])
            index += 1

    ## The core logic the character uses to move
    def how_to_move(self):
        print("Character.how_to_move - "
        + str(self.squad_size \
        - (self.squad_size*25/100)) \
        + " > " + str(self.number_of_close_enemies))
        if(self.health <= self.maxHealth*30/100):
            if((self.squad_size \
            - round(self.squad_size*25/100)) \
             > self.number_of_close_enemies):
                if(self.health <= self.maxHealth*10/100):
                    self.run_away()
                else:
                    if(len(self.enemies)>0):
                        self.pursue()
            else:
                self.run_away()
        else:
            if(len(self.enemies)>0):
                self.pursue()

    ## Damage the character's health
    ## unless it is below 0,
    ## in which case it is set to 0
    def damage(self, amount):
        if self.health - amount < 0:
            print("Character.damage - " \
            + str(self.name) + " " \
            + str(self.health) + " - " \
            + str(amount) + " = " \
            + "0")
            self.health = 0
        else:
            print("Character.damage - " \
            + str(self.name) + " " \
            + str(self.health) + " - " \
            + str(amount) + " = " \
            + str(self.health-amount))
            self.health -= amount

    ## Heal the character's health
    ## unless it is above maximum health,
    ## in which case it is set to the maximum
    def heal(self, amount):
        if self.health + amount > self.maxHealth:
            print("Character.heal - " \
            + str(self.name) + " " \
            + str(self.health) + " + " \
            + str(amount) + " = " \
            + str(self.maxHealth))
            self.health = self.maxHealth
        else:
            print("Character.heal - " \
            + str(self.name) + " " \
            + str(self.health) + " + " \
            + str(amount) + " = " \
            + str(self.health+amount))
            self.health += amount

    ## Makes the character find the closest cover
    ## and escape to it
    def run_away(self):
        print("Character.run_away")
        self.find_closest_cover()
        #print("Character.run_away - closest cover: " + str(self.find_closest_cover()))
        #print("Character.run_away - position type: " + str(type(self.position)))
        #print("Character.run_away - closest_cover type: " + str(type(self.closest_cover)))
        #print("Character.run_away - position values: " \
        #+ str((self.position[0])) \
        #+ " " + str((self.position[1])) \
        #+ " " + str((self.position[2])))
        #print("Character.run_away - closest_cover values: " \
        #+ str((self.closest_cover[0])) \
        #+ " " + str((self.closest_cover[1])) \
        #+ " " + str((self.closest_cover[2])))
        self.set_escape_route(shortest_path(self.graph, self.position, (self.run_to_point[0], self.run_to_point[1], self.run_to_point[2]), self.sldist))
        self.move(self.escape_route)

    ## Pursue the enemy, moving to it's position,
    ## in this case, the first enemy in the array
    def pursue(self):
        print("Character.pursue - enemies size " + str(len(self.enemies)))
        self.move(shortest_path(g, self.position,(self.enemies[0].get_pos()[0],self.enemies[0].get_pos()[1],self.enemies[0].get_pos()[2]), sldist))


    ## Find the closest cover
    def find_closest_cover(self):
        #print("Characer.find_closest_cover")
        radius = 1
        limit = 5
        x = self.position[0]-radius
        y = self.position[1]-radius
        z = self.position[2]-radius

        #print("Characer.find_closest_cover - " \
        #+ "closest cover to "
        #+ str(self.position))

        ## Search in a cube
        while (z <= radius + self.position[2] \
        or z >= radius - self.position[2]):
            #print("Characer.find_closest_cover - z " + str(z))
            while (y <= radius + self.position[1] \
            or y >= radius - self.position[1]):
                #print("Characer.find_closest_cover - y " + str(y))
                while (x <= radius + self.position[0] \
                or x >= radius - self.position[0]):
                    #print("Characer.find_closest_cover - radius " + str(radius))
                    #print("Characer.find_closest_cover - (" + str(x)#)
                    #+ "," + str(y)
                    #+ "," + str(z) + ")")

                    if (x,y,z) in g.blocked_nodes:
                        #print("Character.find_closest_cover - " \
                        #+ "Current pos: " \
                        #+ str(self.position) \
                        #+ " || ("
                        #+ str(x) + ","
                        #+ str(y) + ","
                        #+ str(z) + ") in blocked_nodes")

                        ## Set the closest cover to the matching position
                        self.closest_cover = (x,y,z)
                        ## Find the 'closest' free node by the closest cover
                        self.find_closest_free_node(self.closest_cover)

                        radius = limit+1
                        x = self.position[0]-radius
                        y = self.position[1]-radius
                        z = self.position[2]-radius
                        break

        ## The following increments the axis points and resets them,
        ## depending on the current values
                    x += 1
                    if x >= radius + self.position[0] or radius > limit:
                        x = self.position[0]-radius
                        y += 1
                        break
                if y >= radius + self.position[1] or radius > limit:
                    y = self.position[1]-radius
                    z += 1
                    break
            if z >= radius + self.position[2] or radius > limit:
                #print("Character.find_closest_path - " \
                #+ "resetting xyz")
                if radius >= limit:
                    #print("Character.find_closest_path - " \
                    #+ "limit reached")
                    break
                radius += 1
                x = self.position[0]-radius
                y = self.position[1]-radius
                z = self.position[2]-radius
                    #print("Characer.find_closest_cover - " \
                    #+ "Making cube bigger " + str(radius))

    ## Find the closest free node by the given node
    def find_closest_free_node(self, inNode):
        ## If the node is blocked subtract one from the x axis
        ## then recursively recall this function
        ## until a non-blocked node is found
        if(inNode in g.blocked_nodes):
            #self.run_to_point[0] -= 1
            self.find_closest_free_node((inNode[0]-1,inNode[1],inNode[2]))
            #self.run_to_point = (x,inNode[1], inNode[2])
        else:
            self.run_to_point = (inNode[0],inNode[1], inNode[2])

    ##
    ## The following are some getters and setters
    ##
    def get_name(self):
        return self.name

    def set_escape_route(self, route):
        self.escape_route = route

    def get_escape_route(self):
        return self.escape_route

    def get_closest_cover(self):
        return self.closest_cover

    def get_pos(self):
        return self.position

    def set_graph(self, inG):
        self.graph = inG

    def set_sldist(self, inSldist):
        self.sldist = inSldist

    def set_enemy(self, inCharacter):
        self.enemy = inCharacter

    def set_number_of_close_allies(self, inNumber):
        self.number_of_close_allies = inNumber

    ## Check surrounding nodes for any characters
    ## similar to the above cube searching (the method find_closest_cover)
    def check_for_surrounding_characters(self, radius):
        x = self.position[0]-radius
        y = self.position[1]-radius
        z = self.position[2]-radius

        #print("Characer.find_closest_cover - " \
        #+ "closest cover to "
        #+ str(self.position))
        #print("Character.check_surrounding_nodes - loop pos(" + str(x)#)
        #+ "," + str(y)
        #+ "," + str(z) + ")")


        for z in range (self.position[2] - radius, radius + self.position[2]):
            #print("Characer.find_closest_cover - z " + str(z))
            #print(str(radius - self.position[2]) + " " + str(z) + " " + str(radius + self.position[2]))
            for y in range (self.position[1] - radius, radius + self.position[1]):
                #print("Characer.find_closest_cover - y " + str(y))
                for x in range (self.position[0] - radius, radius + self.position[0]):
                    #print("Characer.find_closest_cover - radius " + str(radius))

                    ## Makes sure the point is not character's position
                    if self.position != (x,y,z):
                        #print("Character.check_surrounding_nodes - loop pos(" + str(x)#)
                        #+ "," + str(y)
                        #+ "," + str(z) + ")"
                        #+ " char pos(" + str(self.position[0])#)
                        #+ "," + str(self.position[1])
                        #+ "," + str(self.position[2]) + ")")

                        ## Check for a character at the current point
                        ## and check its faction, to know which array to add the character to
                        ## make number of allies/enemies the size of the respective arrays
                        if (character_at((x,y,z), self.faction, "faction")) == "friendly":
                            self.allies.append(character_at((x,y,z), self.faction, "character"))
                            self.number_of_close_allies = len(self.allies)
                            self.squad_size = self.number_of_close_allies + 1
                        if (character_at((x,y,z), self.faction, "faction")) == "enemy":
                            self.enemies.append(character_at((x,y,z), self.faction, "character"))
                            self.number_of_close_enemies = len(self.enemies)

                    x += 1
                    if x >= radius + self.position[0]:
                        x = self.position[0]-radius
                        y += 1
                        break
                if y >= radius + self.position[1]:
                    y = self.position[1]-radius
                    z += 1
                    break
            if z >= radius + self.position[2]:
                #print("Character.find_closest_path - " \
                #+ "resetting xyz")
                #if radius >= limit:
                    #print("Character.find_closest_path - " \
                    #+ "limit reached")
                break
                z = self.position[2]-radius

## Checks if there is a character at a specific point, with a specific faction,
## the switch is a string to know whether to return the faction of the character
## or to return the character itself
def character_at(inPos, inFaction, switch):
    #print("character_at - params: " + str(inPos) + " " + str(inFaction))
    if switch == "faction":
        for a in characters:
            #print("character_at - character: "  + a.get_name() + " " + str(a.get_pos()) + " " + str(a.faction))
            if a.get_pos() == inPos \
            and a.faction == inFaction:
                #print("character_at - match found "  + a.get_name() + " " + str(a.get_pos()) + " " + str(a.faction))
                return "friendly"
            if a.get_pos() == inPos \
            and a.faction != inFaction:
                #print("character_at - match found "  + a.get_name() + " " + str(a.get_pos()) + " " + str(a.faction))
                return "enemy"

        #print("character_at - No friendlies found")
        return False
    if switch == "character":
        for b in characters:
            #print("character_at - character: "  + a.get_name() + " " + str(a.get_pos()) + " " + str(a.faction))
            if b.get_pos() == inPos:
                return b

## The sizes of the cube grid
xSize = 10
ySize = 10
zSize = 10

## The main function, runs at launch
if __name__ == '__main__':
    import math

    ## A heuristic value
    sldist = lambda c1, c2: math.sqrt((c2[0] - c1[0])**2 + (c2[1] - c1[1])**2)
    ## Makes a new graph object
    g = Graph()

    ## Generates a 3D grid with the size of the values
    for a in range(xSize):
        for b in range(ySize):
            for c in range(zSize):
                g.add_node((a, b, c))

    ## The following is to add all the connections between the nodes
    for c in range(zSize):
        for b in range(ySize):
            for a in range(xSize):
                g.add_edge((a,b,c), (a+1, b, c), 1.0)
                #print("(" + str(a) + "," + str(b) + "," + str(c) + ") to" + " (" + str((a+1)) + "," + str((b)) + "," + str((c)) + ")")

        for b in range(ySize):
            for a in range(xSize):
                g.add_edge((a,b,c), (a, b+1, c), 1.0)
                #print("(" + str(a) + "," + str(b) + "," + str(c) + ") to" + " (" + str((a)) + "," + str((b+1)) + "," + str((c)) + ")")

        for b in range(ySize):
            for a in range(xSize):
                g.add_edge((a,b,c), (a, b, c+1), 1.0)
                #print("(" + str(a) + "," + str(b) + "," + str(c) + ") to" + " (" + str((a)) + "," + str((b)) + "," + str((c+1)) + ")")

        for b in range(ySize):
            for a in range(xSize):
                g.add_edge((a,b,c), (a, b+1, c-1), 1.25)
                #print("(" + str(a) + "," + str(b) + "," + str(c) + ") to" + " (" + str((a)) + "," + str((b+1)) + "," + str((c-1)) + ")")

        for b in range(ySize):
            for a in range(xSize):
                g.add_edge((a,b,c), (a-1, b-1, c), 1.25)
                #print("(" + str(a) + "," + str(b) + "," + str(c) + ") to" + " (" + str((a-1)) + "," + str((b-1)) + "," + str((c)) + ")")

        for b in range(ySize):
            for a in range(xSize):
                g.add_edge((a,b,c), (a-1, b+1, c), 1.25)
                #print("(" + str(a) + "," + str(b) + "," + str(c) + ") to" + " (" + str((a-1)) + "," + str((b+1)) + "," + str((c)) + ")")

        for b in range(ySize):
            for a in range(xSize):
                g.add_edge((a,b,c), (a-1, b, c+1), 1.25)
                #print("(" + str(a) + "," + str(b) + "," + str(c) + ") to" + " (" + str((a-1)) + "," + str((b)) + "," + str((c+1)) + ")")

        for b in range(ySize):
            for a in range(xSize):
                g.add_edge((a,b,c), (a, b+1, c+1), 1.25)
                #print("(" + str(a) + "," + str(b) + "," + str(c) + ") to" + " (" + str((a)) + "," + str((b+1)) + "," + str((c+1)) + ")")

        for b in range(ySize):
            for a in range(xSize):
                g.add_edge((a,b,c), (a+1, b, c+1), 1.25)
                #print("(" + str(a) + "," + str(b) + "," + str(c) + ") to" + " (" + str((a+1)) + "," + str((b)) + "," + str((c+1)) + ")")

        for b in range(ySize):
            for a in range(xSize):
                g.add_edge((a,b,c), (a-1, b+1, c+1), 1.5)
                #print("(" + str(a) + "," + str(b) + "," + str(c) + ") to" + " (" + str((a-1)) + "," + str((b+1)) + "," + str((c+1)) + ")")

        for b in range(ySize):
            for a in range(xSize):
                g.add_edge((a,b,c), (a-1, b-1, c+1), 1.5)
                #print("(" + str(a) + "," + str(b) + "," + str(c) + ") to" + " (" + str((a-1)) + "," + str((b-1)) + "," + str((c+1)) + ")")

        for b in range(ySize):
            for a in range(xSize):
                g.add_edge((a,b,c), (a+1, b-1, c+1), 1.5)
                #print("(" + str(a) + "," + str(b) + "," + str(c) + ") to" + " (" + str((a+1)) + "," + str((b-1)) + "," + str((c+1)) + ")")

        for b in range(ySize):
            for a in range(xSize):
                g.add_edge((a,b,c), (a+1, b+1, c+1), 1.5)
                #print("(" + str(a) + "," + str(b) + "," + str(c) + ") to" + " (" + str((a+1)) + "," + str((b+1)) + "," + str((c+1)) + ")")

    #print("g.nodes - " + str(g.nodes))

    ## To add blocked nodes,
    ## follow the code 'guideline' below
    ## still in buggy and in development
    ## works half the time
    #g.add_blocked_node((1,0,0))
    #g.add_blocked_node((1,1,0))
    #g.add_blocked_node((2,0,1))
    #g.add_blocked_node((4,1,1))
    #g.add_blocked_node((2,1,1))
    #g.add_blocked_node((3,3,0))
    #g.add_blocked_node((3,3,1))
    #g.add_blocked_node((3,3,2))
    #g.add_blocked_node((2,3,0))
    #g.add_blocked_node((2,3,1))
    #g.add_blocked_node((2,3,2))
    #g.add_blocked_node((1,3,0))
    #g.add_blocked_node((1,3,1))
    #g.add_blocked_node((1,3,2))

    ## Blocked nodes can also be adding with a node
    ## as demonstrated below
    #for i in range(7):
        #for j in range(7):
            #g.add_blocked_node((0+i,3,0+j))
            #g.add_blocked_node((1+i,4,1))
            #g.add_blocked_node((1+i,4,2))
            #g.add_blocked_node((1,4,3))
            #g.add_blocked_node((2,4,0))
            #g.add_blocked_node((2,4,1))
            #g.add_blocked_node((2,4,2))
            #g.add_blocked_node((2,4,3))
            #g.add_blocked_node((3,4,0))
            #g.add_blocked_node((3,4,1))
            #g.add_blocked_node((3,4,2))
            #g.add_blocked_node((3,4,2))
    #print("blocked_nodes" + str(g.blocked_nodes))

    characters = list()

    ## 'Player' generator, generates X number of 'players'
    player_number = 2

    for i in range(player_number):
        ## Adding i prevents characters being in the same position
        player = Character(("Player" + str(i)), 100, (2,2 ,i+1), "player")
        player.set_graph(g)
        player.set_sldist(sldist)

        characters.append(player)

    ## 'Enemy' generator, generates X number of 'enemies'
    enemy_number = 2

    for i in range(enemy_number):
        enemy = Character(("Enemy" + str(i)), 100, (2,4,1+i), "enemy")
        enemy.set_graph(g)
        enemy.set_sldist(sldist)

        characters.append(enemy)

    ## Loops through all the characters and prints some feedback
    for i in characters:
        i.check_for_surrounding_characters(5)
        print(i.name + " has " + str(i.number_of_close_enemies) + " enemy(s)")
        print(i.name + " has " + str(i.number_of_close_allies) + " ally(s)")
        print(i.name + " has " + str(i.squad_size) + " sqaud mate(s)")

    ## The following forces a character to move
    #enemy.move_to((5,5,5))
    ## The following forces the number of allies
    #enemy1.set_number_of_close_allies(5)
    ## The following finds the closest cover
    #enemy1.find_closest_cover()
    ## The following makes the character run away
    #enemy1.run_away()
    #print(str(enemy1.get_escape_route()))

    for i in characters:
        if i.faction == "enemy":
            ## Damages the character
            ## used to test the pursue/run away logic
            i.damage(85)
            ## Launches the main logic
            i.how_to_move()
            ## Makes it only find one enemy
            break

    #print("number of nodes:" + str(len(g.nodes)))