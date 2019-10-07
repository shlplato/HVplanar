# -*- coding: utf-8 -*-
"""
Created on Wed Dec 05 15:30:49 2018

@author: olechrs

###########################################################################
# Simulation FEMM lancé par Matlab. Il faut spécifier la géometrie
# des spires (16 valeur) du transformateur où le primaire et le secondaire
# sont fabriqués comme des circuits imprimés, geoemtrie[16].


        Matrices: index 1 pour le primaire (en haut),
                    index 2 pour le secondaire (en bas)

        |                    l_cuivre        l_cuivre
        |                   <----> l_entre <---->
        |<--r_interieur(1)-> ____ <-------> ____        no_sp_prim == 2
        |___________________|____|_________|____|_____
 y=0___|_____________________________________________| ep_pcb
        |                           |    |  /\
        |                            |____|  \/ep_cuivre
        |<-----r_interieur(2)------>                no_sp_sec == 1
        |
        |<---------------r_pcb------------------------>
        |
 l'axe de symétrie

###########################################################################
"""

import femm
from math import pi
import numpy as np
import matplotlib.pyplot as plt


def initial_setup(limite_externe, voltage_high):
    # Commandes liés au logiciel pour acceder toutes les commandes FEMM
    # Les commandes prochaines sont lancé par le fichier principal de
    # l'algorithme génétique pour eviter des éxecuter plusieurs fois. En plus,
    # le fichier openfemm.m est modifié pour éviter que la fenêtre FEMM
    # travaille à l'arrière-plan: le drapeu '-windowhide' est ajouté à la
    # commande au système.
    femm.openfemm(1)
    # mi_minimize()
    # From manual: minimizes the active magnetics input view.
#    femm.main_minimize()

    # newdocument(doctype)
    # From manual: Creates a new preprocessor document and opens up a new
    # preprocessor window. Specify doctype to be 0 for a magnetics problem, 1
    # for an electrostatics problem, 2 for a heat flow problem, or 3 for a
    # current flow problem. An alternative syntax for this command is
    # create(doctype)
    femm.newdocument(1)

    # ei probdef(units,type,precision,(depth),(minangle))
    # From manual: changes the problem definition. The units parameter
    # specifies the units used for measuring length in the problem domain.
    # Valid "units" entries are "inches", "millimeters", "centimeters", "mils",
    # "meters, and "micrometers". Set problemtype to "planar" for a 2-D planar
    # problem, or to "axi" for an axisymmetric problem. The precision parameter
    # dictates the precision required by the solver. For example, entering
    # 1.E-8 requires the RMS of the residual to be less than 10^-8. A fourth
    # parameter, representing the depth of the problem in the into-thepage
    # direction for 2-D planar problems, can also be specified for planar
    # problems. A sixth parameter represents the minimum angle constraint sent
    # to the mesh generator.
    precision = 1e-9
    femm.ei_probdef('millimeters', 'axi', precision, 100, 30)

    # Circuit
    # From manual: ei_addconductorprop("conductorname", Vc, qc, conductortype)
    # adds a new conductor property with name "conductorname" with either a
    # prescribed voltage or a prescribed total charge. Set the unused property
    # to zero. The conductortype parameter is 0 for prescribed charge and 1 for
    # prescribed voltage
    femm.ei_addconductorprop('high', voltage_high, 0, 1)
    femm.ei_addconductorprop('zero', 0, 0, 1)

    # Trace de la geometrie
    # ei_drawrectangle(x1, y1, x2, y2)
    # From manual: no discription

    # ei selectsegment(x,y)
    # From manual: Select the line segment closest to (x,y)

    # ei_setsegmentprop("propname", elementsize, automesh, hide,
    #                   group, "inconductor",)
    # From manual: Set the select segments to have:
    # Boundary property "propname"
    # Local element size along segment no greater than elementsize
    # automesh: 0 = mesher defers to the element constraint defined by
    # elementsize, 1 = mesher automatically chooses mesh size along the
    # selected segments
    # hide: 0 = not hidden in post-processor, 1 == hidden in post processor
    # A member of group number group
    # A member of the conductor specified by the string "inconductor". If the
    # segment is not part of a conductor, this parameter can be specified as
    # "<None>".

    # Materiaux
    # ei_addmaterial(’matname’, ex, ey, qv)
    # From manual: adds a new material with called ’matname’ with the material
    # properties:
    # ex Relative permittivity in the x- or r-direction.
    # ey Relative permittivity in the y- or z-direction.
    # qv Volume charge density in units of C/m3
    femm.ei_addmaterial('air', 1, 1, 0)
    femm.ei_addmaterial('FR4', 4.4, 4.4, 0)
    femm.ei_addmaterial('Polysterimide', 3.5, 3.5, 0)
    femm.ei_addmaterial('Teflon', 2.1, 2.1, 0)
    femm.ei_addmaterial('Silgel', 2.7, 2.7, 0)
    femm.ei_addmaterial('Midel', 3.15, 3.15, 0)
    femm.ei_addmaterial('Epoxy', 10, 10, 0)

    # Conditions limites
    # ei makeABC(n,R,x,y,bc)
    # From manual: creates a series of circular shells that emulate the
    # impedance of an unbounded domain (i.e. an Improvised Asymptotic Boundary
    # Condition). The n parameter contains the number of shells to be used
    # (should be between 1 and 10), R is the radius of the solution domain, and
    # (x,y) denotes the center of the solution domain. The bc parameter should
    # be specified as 0 for a Dirichlet outer edge or 1 for a Neumann outer
    # edge. If the function is called without all the parameters, the function
    # makes up reasonable values for the missing parameters.
    femm.ei_makeABC(7, limite_externe, 0, 0, 0)


def translate_geometry(g):
    ''' Translates from old to new style of handling geometry parameters '''
    geometry = []
    geometry.append(g.turns_primary)
    geometry.append(g.layers_primary)
    geometry.append(g.turns_secondary)
    geometry.append(g.layers_secondary)
    geometry.append(g.height_pcb_core)
    geometry.append(g.height_pcb_prepreg)
    geometry.append(g.height_dielectric)
    geometry.append(g.height_copper)
    geometry.append(g.width_copper)
    geometry.append(g.radius_inner_track)
    geometry.append(g.width_between_tracks)
    geometry.append(g.radius_pcb)
    geometry.append(g.radius_dielectric)
    if g.material_dielectric == 'fr4':
        geometry.append(1)
    elif g.material_dielectric == 'polysterimide':
        geometry.append(2)
    elif g.material_dielectric == 'teflon':
        geometry.append(3)
    else:
        geometry.append(-1)
        print('Error: cannot translate material name: {}'.format(
              g.material_dielectric))
    geometry.append(g.height_gap)
    geometry.append(g.height_gel)
    geometry.append(g.radius_gel)
    return geometry


def set_conductor_boundry(coords, volt):
    '''
    Set voltage of the four sides of a square conductor to either 0 or 1 V
    INPUT: corner, length and height of conductor
    '''
    # ei_selectsegment(x,y)
    # From manual: Select the line segment closest to (x,y)
    femm.ei_selectsegment(coords[0], np.average((coords[1], coords[3])))
    femm.ei_selectsegment(np.average((coords[0], coords[2])), coords[1])
    femm.ei_selectsegment(coords[2], np.average((coords[1], coords[3])))
    femm.ei_selectsegment(np.average((coords[0], coords[2])), coords[3])
    if volt == 1:
        femm.ei_setsegmentprop('<None>', 0, 1, 0, 0, 'high')
    elif volt == 0:
        femm.ei_setsegmentprop('<None>', 0, 1, 0, 0, 'zero')
    femm.ei_clearselected()


def set_conductor_label(coords, label_name, label_dict):
    '''
    Set a block label inside a square conductor, and give the block label
    properties. INPUT: corner, length and height of conductor, label name and
    label dictionary
    '''
    # ei_addblocklabel(x,y)
    # From manual: Add a new block label at (x,y)
    label_coord = (np.average((coords[0], coords[2])),
                   np.average((coords[1], coords[3])))
    femm.ei_addblocklabel(*label_coord)
    label_dict[label_name] = label_coord
    return label_dict


def draw_conductor(coords, in_conductor, label_name, label_dict):
    ''' Draw rectabngualr shapeof conducture in problem and add label '''
    femm.ei_drawrectangle(*coords)
    # ajouter la tension pour les trace du bobinage du primaire
    set_conductor_boundry(coords, in_conductor)
    # label du bobinage du primaire
    label_dict = set_conductor_label(coords, label_name, label_dict)
    return label_dict


def add_conductors(geometry, z0, dz, label_dict):
    ''' Add all conductors of a pcb to the problem '''
    no_spires_prim = geometry[0]
    no_couches_prim = geometry[1]
    no_spires_sec = geometry[2]
    no_couches_sec = geometry[3]
    ep_cuivre = geometry[7]
    l_cuivre = geometry[8]
    r_interieur = geometry[9]
    l_entre = geometry[10]

    ep_couches = get_height_between_layers(no_couches_prim, z0[0], dz)
    for c in range(no_couches_prim):
        for i in range(no_spires_prim):
            # coordiantes of conductor
            coords_conductor = coords_of_rectangle(r_interieur[0] +
                                                   (l_entre[0] + l_cuivre) * i,
                                                   ep_couches[c], l_cuivre,
                                                   ep_cuivre)
            # desiner la conductrice, ajouter la tension  et le label
            label_dict = draw_conductor(coords_conductor, 1,
                                        'prim' + str(i + c * no_spires_prim),
                                        label_dict)
    # définition du bobinage du secondaire
    ep_couches = get_height_between_layers(no_couches_prim, z0[1], -dz)
    for c in range(no_couches_sec):
        for i in range(no_spires_sec):
            coords_conductor = coords_of_rectangle(r_interieur[1] +
                                                   (l_entre[1] + l_cuivre) * i,
                                                   ep_couches[c], l_cuivre,
                                                   -ep_cuivre)
            # desiner la conductrice, ajouter la tension  et le label
            label_dict = draw_conductor(coords_conductor, 0,
                                        'sec' + str(i + c * no_spires_sec),
                                        label_dict)


def round_conductor_edges(geometry, label_dict):
    ''' round the edges of conductors that are critical to the peak field
    calculations. These conductors will be the ones closest to the dielectric
    material, and both inner and outer conductor corners
    geometry - geometry of transformer problem
    label_dict - label dictionary for all transformer elements
    '''
    # Define parameters of the rounding
    turns = geometry[0]
    conductor_height = geometry[7]
    conductor_width = geometry[8]
    corner_radius = .2 * conductor_height  # percentage of conductor height
    segment_length = 0.004

    # Find primary side corners and add new labels for the rounded edge
    label_dict['edge0'] = (np.array(label_dict['prim0']) +
                           np.array((-conductor_width, -conductor_height))/2.0)
    label_dict['edge1'] = (np.array(label_dict['prim' + str(turns - 1)]) +
                           np.array((conductor_width, -conductor_height))/2.0)
    # Find secondary side corners and add new labels for the rounded edge
    label_dict['edge2'] = (np.array(label_dict['sec0']) +
                           np.array((-conductor_width, conductor_height))/2.0)
    label_dict['edge3'] = (np.array(label_dict['sec' + str(turns - 1)]) +
                           np.array((conductor_width, conductor_height))/2.0)
    # Round edges and set arcsegment properties
    for e in ['edge0', 'edge1']:
        corner = label_dict[e]
        femm.ei_createradius(corner[0], corner[1], corner_radius)
        femm.ei_selectarcsegment(*corner)
        femm.ei_setarcsegmentprop(1, '<None>', 0, 0, 'high')
    for e in ['edge2', 'edge3']:
        corner = label_dict[e]
        femm.ei_createradius(corner[0], corner[1], corner_radius)
        femm.ei_selectarcsegment(*corner)
        femm.ei_setarcsegmentprop(1, '<None>', 0, 0, 'zero')
    increase_pcb_mesh(conductor_height, conductor_height*2, segment_length,
                      label_dict)


def trapezoidal_conductor_edges(geometry, label_dict):
    ''' make the edges of conductors trapezoidal for those that are critical to
    the peak field calculations. These conductors will be the ones closest to
    the dielectric material, and both inner and outer conductor corners.
    geometry - geometry of transformer problem
    label_dict - label dictionary for all transformer elements
    '''
    # Define parameters of the rounding
    turns = geometry[0]
    conductor_height = geometry[7]
    conductor_width = geometry[8]
    cut_in_length = 2 * conductor_height  # percentage of conductor height
    corner_radius = 1.7 * conductor_height
    ledge_height = 0.005
    ledge_radius = 0.004
    segment_length = 0.004
    angle_max = 1

    # Make trapezaoidal corners on primary side corners and add new labels for
    # the new points. Sequence: -> find corner to be moved -> set segment props
    # -> make ledge -> move corner to make trapezoid -> add nodes for edge and
    # edge corner -> repeat for all corners -> set all segment props -> round
    # all edges -> set all arcsegment props -> set segment props along pcb for
    # all trapezoidal conductor edges.

    # Primary inner corner
    inner_corner = (np.array(label_dict['prim0']) +
                    np.array((-conductor_width/2., -conductor_height/2.)))
    femm.ei_selectsegment(*(inner_corner + np.array((0, conductor_height/2.))))
    femm.ei_setsegmentprop('<None>', segment_length, 0, 0, 0, 'high')
    label_dict['ledge0corner'] = (inner_corner +
                                  np.array((0, conductor_height-ledge_height)))
    femm.ei_addnode(*label_dict['ledge0corner'])
    femm.ei_selectnode(*inner_corner)
    femm.ei_movetranslate(cut_in_length, 0)
    label_dict['edge0'] = (np.array(label_dict['prim0']) +
                           np.array(((-conductor_width+cut_in_length)/2., 0)))
    label_dict['edge0corner'] = inner_corner + np.array((cut_in_length, 0))
    # Primary outer corner
    outer_corner = (np.array(label_dict['prim' + str(turns - 1)]) +
                    np.array((conductor_width/2., -conductor_height/2.)))
    femm.ei_selectsegment(*(outer_corner + np.array((0, conductor_height/2.))))
    femm.ei_setsegmentprop('<None>', segment_length, 0, 0, 0, 'high')
    label_dict['ledge1corner'] = (outer_corner +
                                  np.array((0, conductor_height-ledge_height)))
    femm.ei_addnode(*label_dict['ledge1corner'])
    femm.ei_selectnode(*outer_corner)
    femm.ei_movetranslate(-cut_in_length, 0)
    label_dict['edge1'] = (np.array(label_dict['prim' + str(turns - 1)]) +
                           np.array(((conductor_width-cut_in_length)/2., 0)))
    label_dict['edge1corner'] = outer_corner + np.array((-cut_in_length, 0))

    # Secondary inner corner
    inner_corner = (np.array(label_dict['sec0']) +
                    np.array((-conductor_width/2., conductor_height/2.)))
    femm.ei_selectsegment(*(inner_corner +
                            np.array((0, -conductor_height/2.))))
    femm.ei_setsegmentprop('<None>', segment_length, 0, 0, 0, 'zero')
    label_dict['ledge2corner'] = (inner_corner +
                                  np.array((0, ledge_height-conductor_height)))
    femm.ei_addnode(*label_dict['ledge2corner'])
    femm.ei_selectnode(*inner_corner)
    femm.ei_movetranslate(cut_in_length, 0)
    label_dict['edge2'] = (np.array(label_dict['sec0']) +
                           np.array(((-conductor_width+cut_in_length)/2., 0)))
    label_dict['edge2corner'] = inner_corner + np.array((cut_in_length, 0))
    # Secondary outer corner
    outer_corner = (np.array(label_dict['sec' + str(turns - 1)]) +
                    np.array((conductor_width/2., conductor_height/2.)))
    femm.ei_selectsegment(*(outer_corner +
                            np.array((0, -conductor_height/2.))))
    femm.ei_setsegmentprop('<None>', segment_length, 0, 0, 0, 'zero')
    label_dict['ledge3corner'] = (outer_corner +
                                  np.array((0, ledge_height-conductor_height)))
    femm.ei_addnode(*label_dict['ledge3corner'])
    femm.ei_selectnode(*outer_corner)
    femm.ei_movetranslate(-cut_in_length, 0)
    label_dict['edge3'] = (np.array(label_dict['sec' + str(turns - 1)]) +
                           np.array(((conductor_width-cut_in_length)/2., 0)))
    label_dict['edge3corner'] = outer_corner + np.array((-cut_in_length, 0))

    # Set segment size for diagonal line to decrease mesh sizing
    femm.ei_selectsegment(*label_dict['edge0'])
    femm.ei_selectsegment(*label_dict['edge1'])
    femm.ei_setsegmentprop('<None>', segment_length, 0, 0, 0, 'high')
    femm.ei_clearselected()
    femm.ei_selectsegment(*label_dict['edge2'])
    femm.ei_selectsegment(*label_dict['edge3'])
    femm.ei_setsegmentprop('<None>', segment_length, 0, 0, 0, 'zero')
    femm.ei_clearselected()

    # Round new edge on primary and secondary and set arcangle
    for idx in range(4):
        node = label_dict['edge' + str(idx) + 'corner']
        femm.ei_createradius(node[0], node[1], corner_radius)
        node = label_dict['ledge' + str(idx) + 'corner']
        femm.ei_createradius(node[0], node[1], ledge_radius)
    # Set arcsegment properties
    segments = [str(x) + str(y) + 'corner' for x in ['edge', 'ledge']
                for y in range(2)]
    for s in segments:
        femm.ei_selectarcsegment(*label_dict[s])
    femm.ei_setarcsegmentprop(angle_max, '<None>', 0, 0, 'high')
    femm.ei_clearselected()

    segments = [str(x) + str(y) + 'corner' for x in ['edge', 'ledge']
                for y in range(2, 4)]
    for s in segments:
        femm.ei_selectarcsegment(*label_dict[s])
    femm.ei_setarcsegmentprop(angle_max, '<None>', 0, 0, 'zero')
    femm.ei_clearselected()

    # Set segment size to decrease mesh size along edge of PCB where the field
    # is high
    increase_pcb_mesh(cut_in_length, conductor_height, segment_length,
                      label_dict)


def increase_pcb_mesh(cut_in, dz, segment_length, label_dict):
    ''' Set segment size to decrease mesh size along edge of PCB where the
    field is high'''
    pcb_segment = []
    pcb_node = []
    pcb_node.append((np.array(label_dict['edge0']) +
                    np.array((-cut_in*1.5, dz/2.))))
    pcb_segment.append(pcb_node[-1] + np.array((cut_in/2., 0)))
    pcb_node.append((np.array(label_dict['edge1']) +
                    np.array((cut_in*1.5, dz/2.))))
    pcb_segment.append(pcb_node[-1] + np.array((-cut_in/2., 0)))
    pcb_node.append((np.array(label_dict['edge2']) +
                    np.array((-cut_in*1.5, -dz/2.))))
    pcb_segment.append(pcb_node[-1] + np.array((cut_in/2., 0)))
    pcb_node.append((np.array(label_dict['edge3']) +
                    np.array((cut_in*1.5, -dz/2.))))
    pcb_segment.append(pcb_node[-1] + np.array((-cut_in/2., 0)))

    for idx, node in enumerate(pcb_node):
        femm.ei_addnode(*node)
        label_dict['edge' + str(idx) + 'pcb'] = node

    for segment in pcb_segment:
        femm.ei_selectsegment(*segment)
    femm.ei_setsegmentprop('<None>', segment_length, 0, 0, 0, '<None>')
    femm.ei_clearselected()


def add_guard(geometry, guard, label_dict):
    ''' Add guard ring(s) in the problem and add a label.
    geometry - geometry list of the transformer
    guard - Guard object
    label_dict - name of the label dictionary
    '''
    if isinstance(guard, (list, tuple)):
        for idx, g in enumerate(guard):
            if g.gtype == 'Ring':
                draw_guard_ring(g.distance, g.gap, g.radius, g.polarity,
                                'guard' + str(idx), label_dict)
            elif g.gtype == 'Trench':
                draw_guard_trench(geometry, g, 'trench' + str(idx), label_dict)
    else:
        if guard.gtype == 'Ring':
                draw_guard_ring(guard.distance, guard.gap, guard.radius,
                                guard.polarity, 'guard0', label_dict)
        elif guard.gtype == 'Trench':
            draw_guard_trench(geometry, guard, 'trench0', label_dict)


def draw_guard_ring(distance, gap, radius, polarity, label_name, label_dict):
    ''' Draw circular shape of guard ring in the problem and add a label.
    distance - distance in r-plane from edge of PCB to edge of guard ring
    gap - distance in z-plane from edge of PCB to edge of guard ring
    radius- radius of the guard ring conductor
    polarity - attach the gaurd ring to high side or low side. Positive
    polarity sets the guard ring to the upper side of the dielectric and adds
    it ot the "high" conductor
    label_name - name of this conductor that is stored in the label dictionary
    label_dict - dictionary that stores label coordinates
    '''
    max_angle = 1
    # high or low side?
    if polarity > 0:
        origin = label_dict['PCB_prim']
        origin = np.array((origin[2], origin[1]))
        point1 = origin + np.array((radius + distance, gap))
        point2 = point1 + np.array((0, 2 * radius))
        in_conductor = 'high'
    else:
        origin = label_dict['PCB_sec']
        origin = np.array((origin[2], origin[1]))
        point1 = origin + np.array((radius + distance, -gap))
        point2 = point1 + np.array((0, -2 * radius))
        in_conductor = 'zero'
    label_dict[label_name + 'surface'] = point1

    # ei_drawarc(x1,y1,x2,y2,angle,maxseg)
    # From manual: Adds nodes at (x1,y1) and (x2,y2) and adds an arc of the
    # specified angle and discretization connecting the nodes.
    femm.ei_drawarc(point1[0], point1[1], point2[0], point2[1], 180, max_angle)
    femm.ei_addarc(point2[0], point2[1], point1[0], point1[1], 180, max_angle)

    # Add label and block property to guard ring
    label_coord = np.average((point1, point2), axis=0)
    femm.ei_addblocklabel(*label_coord)
    femm.ei_selectlabel(*label_coord)
    femm.ei_setblockprop('<No Mesh>', 1, 0, 'guards')
    femm.ei_clearselected()
    label_dict[label_name] = label_coord

    # Set boundry based on coordinates
    # ei_setarcsegmentprop(maxsegdeg, ’propname’, hide, group, ’inconductor’)
    # From manual: Set the selected arc segments to:
    # Meshed with elements that span at most maxsegdeg degrees per element
    # Boundary property ’propname’
    # hide: 0 = not hidden in post-processor, 1 == hidden in post processor
    # A member of group number group
    # A member of the conductor specified by the string ’inconductor’. If the
    # segment is not part of a conductor, this parameter can be specified
    # as ’<None>’.
    femm.ei_selectarcsegment(label_coord[0] - radius, label_coord[1])
    femm.ei_selectarcsegment(label_coord[0] + radius, label_coord[1])
    femm.ei_setarcsegmentprop(max_angle, 'None', 0, 'None', in_conductor)
    femm.ei_clearselected()


def draw_guard_trench(geometry, trench, label_name, label_dict):
    '''
    Draw a trench on the outside of turn closest to the dielectric. The trench
    is defined by the GuardTrench class. The trench is drawn on the upper side
    if polarity is higher than 0. Else, it is drawn on the bottom.
    '''
    conductor_height = geometry[7]
    conductor_width = geometry[8]
    max_angle = 2
    elementsize = 0.05
    if trench.inner:
        sign = -1
        turns = 1
    else:
        sign = 1
        turns = geometry[0]

    # find starting point
    if trench.polarity:
        node0 = (np.array(label_dict['prim' + str(turns - 1)]) +
                 np.array((conductor_width*sign, conductor_height))/2.0 +
                 np.array((trench.distance * sign, 0)))
        in_conductor = 'high'
        pm = 1  # polarity multiplier
    else:
        node0 = (np.array(label_dict['sec' + str(turns - 1)]) +
                 np.array((conductor_width*sign, -conductor_height))/2.0 +
                 np.array((trench.distance * sign, 0)))
        in_conductor = 'zero'
        pm = -1  # polarity multiplier
    # draw four/five points and lines between points 1 to last to 0
    nodes = [(0, 0), (trench.width*sign, 0),
             (trench.width*sign, trench.depth * pm), (0, trench.depth * pm)]
    if trench.drill_angle > 90:
        alpha = (1.0 - trench.drill_angle/180.) * pi
        depth_added = trench.width / (2.0 * np.tan(alpha))
        nodes.insert(-1, (trench.width/2.0*sign,
                          (trench.depth + depth_added) * pm))
    nodes = [node0 + np.array(n) for n in nodes]
    for idx, n in enumerate(nodes):
        femm.ei_addnode(*n)
        label_dict[label_name + 'node'+str(idx)] = n
    ind = range(1, len(nodes)) + [0, ]
    segment_gen = (np.concatenate((nodes[ind[idx]], nodes[ind[idx+1]]))
                   for idx in range(len(nodes)-1))
    for n in segment_gen:
        femm.ei_addsegment(*n)
        femm.ei_selectsegment(*(np.mean((n[:2], n[2:]), axis=0)))
    femm.ei_setsegmentprop('None', elementsize, 0, 0, 'None', in_conductor)
    femm.ei_clearselected()
    # remove existing segment of the PCB
    femm.ei_selectsegment(*(np.mean((nodes[0:2]), axis=0)))
    femm.ei_deleteselectedsegments()
    # draw circular top
    if (pm == 1 and sign == 1) or (pm == -1 and sign == -1):
        femm.ei_addarc(nodes[0][0], nodes[0][1], nodes[1][0], nodes[1][1],
                       trench.outer_angle, max_angle)
    else:
        femm.ei_addarc(nodes[1][0], nodes[1][1], nodes[0][0], nodes[0][1],
                       trench.outer_angle, max_angle)

    # set conductor properties on the boundries
    femm.ei_selectarcsegment(*(np.mean((nodes[0:2]), axis=0)))
    femm.ei_setarcsegmentprop(max_angle, 'None', 0, 'None', in_conductor)

    # add label and set material
    label_dict[label_name] = (nodes[0] +
                              np.array((trench.width/2.*sign,
                                        trench.depth*pm/2.)))
    femm.ei_addblocklabel(*label_dict[label_name])
    femm.ei_selectlabel(*label_dict[label_name])
    femm.ei_setblockprop(trench.material, 1, 0, 'None')
    femm.ei_clearselected()


def get_height_between_layers(no_layers, initial_value, d_height):
    '''
    return an array with the height between copper layers in the PCB depending
    on the number of layers and geometry parameters
    '''
    if no_layers == 1:
        height = (initial_value,)
    elif no_layers == 2:
        height = (initial_value, initial_value + d_height)
    elif no_layers == 4:
        height = np.cumsum([initial_value] + list(d_height)).tolist()
    else:
        print ('get_height_between_layers(): invalid number of layers')
    return height


def coords_of_rectangle(x0, y0, dx, dy):
    '''
    Return array with the coordinates of the two opposite corners of a
    rectangle. Useful as femm commands don't accept arrays as input.
    '''
    return (x0, y0, x0+dx, y0+dy)


def draw_field_contour(coords_start, coords_end, filename=None):
    # eo_seteditmode(mode)
    # From manual: Sets themode of the postprocessor to point, contour, or area
    # mode. Valid entries for mode are "point", "contour", and "area".
    femm.eo_seteditmode('contour')

    # eo_selectpoint(x,y)
    # From manual: Adds a contour point at the closest input point to (x,y).
    # If the selected point and a previously selected point lie at the ends of
    # an arcsegment, a contour is added that traces along the arcsegment. The
    # selectpoint command has the same functionality as the left-button-click
    # contour point selection when the program is running in interactive mode.
    femm.eo_selectpoint(*coords_start)
    femm.eo_selectpoint(*coords_end)

    # eo_makeplot(PlotType,NumPoints,Filename,FileFormat)
    # From manual: Allows Octave to access to the X-Y plot routines. If only
    # PlotType or only PlotType and NumPoints are specified, the command is
    # interpreted as a request to plot the requested plot type to the screen.
    # If, in addition, the Filename parameter is specified, the plot is instead
    # written to disk to the specified file name as an extended metafile. If
    # the FileFormat parameter is also, the command is instead interpreted as a
    # command to write the data to disk to the specfied file name, rather than
    # display it to make a graphical plot. Valid entries for PlotType are:
    # PlotType Definition
    # 0 V (Voltage)
    # 1 |D| (Magnitude of flux density)
    # 2 D . n (Normal flux density)
    # 3 D . t (Tangential flux density)
    # 4 |E| (Magnitude of field intensity)
    # 5 E . n (Normal field intensity)
    # 6 E . t (Tangential field intensity)
    # Valid file formats are:
    # FileFormat Definition
    # 0 Multi-column text with legend
    # 1 Multi-column text with no legend
    # 2 Mathematica-style formatting
    if filename:
        femm.eo_makeplot(4, 5000, filename, 0)
    else:
        femm.eo_makeplot(4, 5000)

    # eo_clearcontour
    # From manual: Clear a prevously defined contour
    femm.eo_clearcontour()


def skip_last(iterator):
    ''' generator that skips the last entry. Used when reading output from
    contour plots as the final line of the output file is empty '''
    prev = next(iterator)
    for item in iterator:
        yield prev
        prev = item


def read_field_contour_file(filename):
    ''' read csv file of a contour plot. Returns the text string for the units
    in the x and y axis, and the data as two lists [x] [y] '''
    with open(filename, 'r') as f:
        unit_xaxis = f.readline()
        unit_yaxis = f.readline()
        data = []
        for row in skip_last(f):
            a, b, c = row.split('\t')
            data.append([float(a), float(b)])
        return unit_xaxis, unit_yaxis, list(zip(*data))


def get_field_contour_max(filename):
    ''' read contour out file and return the maximum value '''
    unitx, unity, values = read_field_contour_file(filename)
    return np.max(values[1])


def save_field_contour(conductor_height, label_dict, guard=None):
    ''' make field contour plots of critical points in the transformer
    geometry. The critical points are at the inner and outer turn corners as
    well as between the guard rings if included.
    label_dict - dictionary containing label coordinates
    '''
    edge_radius = conductor_height * .2
    # edge0 ++ == upper inner conductor
    # edge1 -+ == upper outer conductor
    # edge2 +- == lower inner conductor
    # edge3 -- == lower outer conductor
    sign = np.array(((1, 1), (-1, 1), (1, -1), (-1, -1)))
    femm.eo_seteditmode('contour')

    for idx in range(4):
        coords = label_dict['edge' + str(idx)]
        contour_start = coords
        contour_stop = coords + (np.array((edge_radius, edge_radius)) *
                                 sign[idx])
        femm.eo_addcontour(*contour_start)
        femm.eo_addcontour(*contour_stop)
        femm.eo_makeplot(4, 5000, '\\output_field_edge' + str(idx) + '.csv', 0)
        femm.eo_clearcontour()

    if guard:
        for idx in range(int(len(guard) / 2)):
            contour_top = np.array(label_dict['guard' + str(idx*2)])
            contour_top += np.array((0, guard[idx*2][2]))
            contour_bottom = np.array(label_dict['guard' + str(idx*2+1)])
            contour_bottom += np.array((0, -guard[idx*2+1][3]))
            fname = '\\output_field_guard' + str(idx) + '.csv'
            draw_field_contour(contour_top, contour_bottom, filename=fname)


def plot_field_contour(filename):
    ''' plot contour output file data '''
    f = plt.figure()
    for f in list(filename):
        unitx, unity, values = read_field_contour_file(f)
        plt.plot(values[0], values[1], linewidth=2)
        plt.xlabel(unitx[unitx.find(':') + 2:])
        plt.ylabel(unity[unity.find(':') + 2:])
    return f


def set_view(view, guard, label_dict):
    for v, l in get_zoom_coords_corners(view, label_dict):
        femm.eo_zoom(*v)
        if view.filename:
            femm.eo_savebitmap(view.filedir + view.filename + l + '.bmp')
    if guard:
        for v, l in get_zoom_coords_guard(view, guard, label_dict):
            femm.eo_zoom(*v)
            if view.filename:
                femm.eo_savebitmap(view.filedir + view.filename + l + '.bmp')
    else:
        # end the view on upper side outer corner if there is no guard,
        # as this is usually the most critical part of the design
        femm.eo_zoom(*get_zoom_coords_corners(view, label_dict)[1][0])


def get_zoom_coords_corners(view, label_dict):
    span = np.array((view.span_r, view.span_z)) / 2.0
    zoom_coords = []
    labels = []
    for label in ['edge'+str(idx) for idx in range(4)]:
        center_point = np.array(label_dict[label])
        labels.append(label)
        zoom_coords.append(np.concatenate((center_point - span,
                                           center_point + span)))
    return zip(zoom_coords, labels)


def get_zoom_coords_guard(view, guard, label_dict):
    zoom_coords = []
    labels = []
    if not isinstance(guard, (list, tuple)):
        guard = [guard, ]
    for idx, g in enumerate(guard):
        span = np.array((view.span_r, view.span_z))
        if g.gtype == 'Ring':
            label = 'guard{}surface'
            if (span < np.array((2*g.radius, g.radius))).all():
                span = np.array((2*g.radius, g.radius)) / 2.0
        elif g.gtype == 'Trench':
            label = 'trench{}'
            if (span < 2 * np.array((g.width, g.depth))).all():
                span = np.array((g.width, g.width*9./16.))
        else:
            span = span / 2.0
        labels.append(label.format(idx))
        center_point = np.array(label_dict[label.format(idx)])
        zoom_coords.append(np.concatenate((center_point - span,
                                           center_point + span)))
    return zip(zoom_coords, labels)


def calc_field_distribution(transformer_geometry, voltage_high=1, view=None):

    # Initiation de parametres
    geometry = translate_geometry(transformer_geometry)
    # Grandeurs de la géometrie
    no_spires_prim = geometry[0]
    no_couches_prim = geometry[1]
    no_spires_sec = geometry[2]
    no_couches_sec = geometry[3]
    ep_pcb_noyau = geometry[4]
    ep_pcb_prepreg = geometry[5]
    ep_dielectric = geometry[6]
    ep_cuivre = geometry[7]
#    l_cuivre = geometry[8]
#    r_interieur = geometry[9]
#    l_entre = geometry[10]
    r_pcb = geometry[11]
    r_dielectrique = geometry[12]
    materiel_dielectrique = geometry[13]
    ep_gap = geometry[14]
    ep_gel = geometry[15]
    r_gel = geometry[16]

    # condition aux limits, limit externe de la simulation
    limits_externes = 2 * r_dielectrique
    # dictionnaire pour gérer les etiquette de la géometrie
    etiquettes_dict = {}

    initial_setup(limits_externes, voltage_high)

    # définition de l'dielectrique
    coords_disc_dielectrique = coords_of_rectangle(0, 0, r_dielectrique,
                                                   ep_dielectric)
    # définition du gel dielectrique
    coords_gel_dielectrique = coords_of_rectangle(0, -ep_gel, r_gel,
                                                  2*ep_gel+ep_dielectric)
    # définition du PCB
    coords_pcb_prim = 0
    coords_pcb_sec = 0
    z0 = (ep_dielectric + ep_gap, -ep_gap)

    # dessiner le bobinage
    if no_couches_prim == 1:
        # print('une couche par PCB')
        # définition du bobinage
        dz = 0
        add_conductors(geometry, z0, dz, etiquettes_dict)

        # définition du PCB au primaire
        coords_pcb_prim = coords_of_rectangle(0, ep_dielectric + ep_cuivre +
                                              ep_gap, r_pcb, ep_pcb_noyau)
        # définition du PCB au secondaire
        coords_pcb_sec = coords_of_rectangle(0, -ep_cuivre - ep_gap, r_pcb,
                                             -ep_pcb_noyau)

    elif no_couches_prim == 2:
        # print('deux couches par PCB')
        # définition du bobinage
        dz = ep_cuivre + ep_pcb_noyau
        add_conductors(geometry, z0, dz, etiquettes_dict)
        # définition du PCB au primaire
        coords_pcb_prim = coords_of_rectangle(0, ep_dielectric + ep_cuivre +
                                              ep_gap, r_pcb, ep_pcb_noyau)
        # définition du PCB au secondaire
        coords_pcb_sec = coords_of_rectangle(0, -ep_cuivre - ep_gap, r_pcb,
                                             -ep_pcb_noyau)

    elif no_couches_prim == 4:
        # print('quatre couches par PCB')
        # définition du bobinage
        dz = np.array((ep_cuivre + ep_pcb_prepreg, ep_cuivre + ep_pcb_noyau,
                       ep_cuivre + ep_pcb_prepreg))
        add_conductors(geometry, z0, dz, etiquettes_dict)
        # définition du isolant au primaire
        coords_pcb_prim = coords_of_rectangle(0, ep_dielectric + ep_cuivre +
                                              ep_gap, r_pcb, ep_pcb_noyau +
                                              2*ep_pcb_prepreg + 3*ep_cuivre)
        # définition du isolant au secondaire
        coords_pcb_sec = coords_of_rectangle(0, -ep_cuivre - ep_gap, r_pcb,
                                             -ep_pcb_noyau - 2*ep_pcb_prepreg -
                                             3*ep_cuivre)
    else:
        'paramètre de couche inconnu'
        return 0

    femm.ei_drawrectangle(*coords_disc_dielectrique)
    femm.ei_drawrectangle(*coords_gel_dielectrique)
    femm.ei_drawrectangle(*coords_pcb_prim)
    femm.ei_drawrectangle(*coords_pcb_sec)
    etiquettes_dict['PCB_prim'] = coords_pcb_prim
    etiquettes_dict['PCB_sec'] = coords_pcb_sec

    if transformer_geometry.edge_type == 'Round':
        round_conductor_edges(geometry, etiquettes_dict)
    elif transformer_geometry.edge_type == 'Trapezoidal':
        trapezoidal_conductor_edges(geometry, etiquettes_dict)

    if transformer_geometry.guard:
        add_guard(geometry, transformer_geometry.guard, etiquettes_dict)

    # mi zoomnatural()
    # From manual: zooms to a “natural” view with sensible extents.
    femm.ei_zoomnatural

    # Ajoute de block labels, étiquettes dans les surfaces
    # ei seteditmode(editmode)
    # From manual: Sets the current editmode to:
    # – "nodes" - nodes
    # – "segments" - line segments
    # – "arcsegments" - arc segments
    # – "blocks" - block labels
    # – "group" - selected group
    femm.ei_seteditmode('blocks')

    # ei addblocklabel(x,y)
    # From manual: Add a new block label at (x,y)

    # label pour le PCB
    coords = [1, ep_gap + ep_dielectric + ep_pcb_noyau / 2.]
    femm.ei_addblocklabel(*coords)
    etiquettes_dict['pcb_prim'] = coords

    coords = [1, - ep_gap - ep_pcb_noyau / 2.]
    femm.ei_addblocklabel(*coords)
    etiquettes_dict['pcb_sec'] = coords

    # label pour l'air autour
    coords = [1, ep_dielectric * 2 + ep_gel]
    femm.ei_addblocklabel(*coords)
    etiquettes_dict['air'] = coords

    # label pour le gel autour
    coords = [r_dielectrique, ep_dielectric + ep_gap + ep_gel / 2.]
    femm.ei_addblocklabel(*coords)
    etiquettes_dict['gel'] = coords

    # label pour l'isolant
    coords = [2, ep_dielectric / 2.]
    femm.ei_addblocklabel(*coords)
    etiquettes_dict['isolant'] = coords

    # Associer blocks avec materiaux
    # ei setblockprop("blockname", automesh, meshsize, group) Set the selected
    # block labels to have the properties: Block property "blockname".
    # automesh: 0 = mesher defers to mesh size constraint defined in meshsize,
    # 1 = mesher automatically chooses the mesh density. meshsize: size
    # constraint on the mesh in the block marked by this label. A member of
    # group number group

    femm.ei_selectlabel(*etiquettes_dict['pcb_prim'])
    femm.ei_selectlabel(*etiquettes_dict['pcb_sec'])
    femm.ei_setblockprop('FR4', 1, 0, 'None')
    femm.ei_clearselected()

    femm.ei_selectlabel(*etiquettes_dict['air'])
    femm.ei_setblockprop('air', 1, 0, 'None')
    femm.ei_clearselected()

    femm.ei_selectlabel(*etiquettes_dict['gel'])
    femm.ei_setblockprop('Midel', 1, 0, 'None')
    femm.ei_clearselected()

    femm.ei_selectlabel(*etiquettes_dict['isolant'])
    if materiel_dielectrique == 1:
        femm.ei_setblockprop('FR4', 1, 0, 'None')
    elif materiel_dielectrique == 2:
        femm.ei_setblockprop('Polysterimide', 1, 0, 'None')
    elif materiel_dielectrique == 3:
        femm.ei_setblockprop('Teflon', 1, 0, 'None')
    femm.ei_clearselected()

    # materiau du bobinage du primaire
    for j in range(no_couches_prim):
        for i in range(no_spires_prim):
            identifier = no_spires_prim * j + i
            femm.ei_selectlabel(*etiquettes_dict['prim' + str(identifier)])
            femm.ei_setblockprop('<No Mesh>', 1, 0, 'phase_prim')
            femm.ei_clearselected()

    # materiau du bobinage du secondaire
    for j in range(no_couches_sec):
        for i in range(no_spires_sec):
            identifier = no_spires_sec * j + i
            femm.ei_selectlabel(*etiquettes_dict['sec' + str(identifier)])
            femm.ei_setblockprop('<No Mesh>', 1, 0, 'phase_sec')
            femm.ei_clearselected()

    # Enregistrement
    femm.ei_saveas('field_calculations.fee')

    # Maillage
    # From manual: Note that it is not necessary to run mesh before performing
    # an analysis, as mi_analyze() will make sure the mesh is up to date before
    # running an analysis.

    # Resolution
    # mi analyze(flag)
    # From manual: runs fkern to solve the problem. The flag parameter controls
    # whether the fkern window is visible or minimized. For a visible window,
    # either specify no value for flag or specify 0. For a minimized window,
    # flag should be set to 1.
    femm.ei_analyze(1)

    # Post-processeur
    femm.ei_loadsolution()

    # eo_showdensityplot(legend,gscale,type,upper D,lower D)
    # From manual: Shows the flux density plot with options:
    # legend Set to 0 to hide the plot legend or 1 to show the plot legend.
    # gscale Set to 0 for a colour density plot or 1 for a grey scale density
    # plot.
    # type Sets the type of density plot. A value of 0 plots voltage, 1 plots
    # the magnitude of D, and 2 plots the magnitude of E
    # upper D Sets the upper display limit for the density plot.
    # lower D Sets the lower display limit for the density plot.
    femm.eo_showdensityplot(1, 0, 2, 50e6 * 20. / 19., 0)

    # Save field lines along outer point of the PCB conductors. If the
    # conductors have trapezoidal shape, it is difficult to estimate where the
    # peak field will be. Hence, the contour lines are not saved.
#    if not edge_trapezoid:
#        save_field_contour(ep_cuivre, etiquettes_dict, guard=guard)
    if view:
        set_view(view, transformer_geometry.guard, etiquettes_dict)

    # eo_getconductorproperties("conductor")Properties are returned for the
    # conductor property named ”conductor”. Two values are returned: The
    # voltage of the specified conductor, and the charge carried on the
    # specified conductor.

    # Calculate the capacitance
    circuit_properties = femm.eo_getconductorproperties('zero')
    charge = -circuit_properties[1]

    # Commands for closing FEMM windows
    # femm.eo_close()
    # femm.ei_close()
    return charge
