/* 
 * PiTiVi
 * Copyright (C) <2004> Edward G. Hervey <hervey_e@epita.fr>
 *                      Guillaume Casanova <casano_g@epita.fr>
 *
 * This software has been written in EPITECH <http://www.epitech.net>
 * EPITECH is a computer science school in Paris - FRANCE -
 * under the direction of Flavien Astraud and Jerome Landrieu.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public
 * License along with this program; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */

#ifndef PITIVI_VIEWERCONTROLLER_H
#define PITIVI_VIEWERCONTROLLER_H

/*
 * Potentially, include other headers on which this header depends.
 */

#include "pitivi-windows.h"
#include "pitivi-viewerwindow.h"

/*
 * Type macros.
 */

#define PITIVI_VIEWERCONTROLLER_TYPE (pitivi_viewercontroller_get_type ())
#define PITIVI_VIEWERCONTROLLER(obj) (G_TYPE_CHECK_INSTANCE_CAST ((obj), PITIVI_VIEWERCONTROLLER_TYPE, PitiviViewerController))
#define PITIVI_VIEWERCONTROLLER_CLASS(klass) (G_TYPE_CHECK_CLASS_CAST ((klass), PITIVI_VIEWERCONTROLLER_TYPE, PitiviViewerControllerClass))
#define PITIVI_IS_VIEWERCONTROLLER(obj) (G_TYPE_CHECK_TYPE ((obj), PITIVI_VIEWERCONTROLLER_TYPE))
#define PITIVI_IS_VIEWERCONTROLLER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE ((klass), PITIVI_VIEWERCONTROLLER_TYPE))
#define PITIVI_VIEWERCONTROLLER_GET_CLASS(obj) (G_TYPE_INSTANCE_GET_CLASS ((obj), PITIVI_VIEWERCONTROLLER_TYPE, PitiviViewerControllerClass))

typedef struct _PitiviViewerController PitiviViewerController;
typedef struct _PitiviViewerControllerClass PitiviViewerControllerClass;
typedef struct _PitiviViewerControllerPrivate PitiviViewerControllerPrivate;

struct _PitiviViewerController
{
  PitiviWindows parent;

  /* instance public members */

  /* private */
  PitiviViewerControllerPrivate *private;
};

struct _PitiviViewerControllerClass
{
  PitiviWindowsClass parent;
  /* class members */
};

/* used by PITIVI_VIEWERCONTROLLER_TYPE */
GType pitivi_viewercontroller_get_type (void);

/*
 * Method definitions.
 */

PitiviViewerController	*pitivi_viewercontroller_new ( PitiviViewerWindow *viewer );

#endif
