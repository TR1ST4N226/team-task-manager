import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd'
import { Plus, X } from 'lucide-react'
import api from '../services/api'
import { taskService } from '../services/taskApi'
import toast from 'react-hot-toast'

const TaskBoard = () => {
  const [columns, setColumns] = useState({
    TODO: { id: 'TODO', title: 'À faire', items: [] },
    IN_PROGRESS: { id: 'IN_PROGRESS', title: 'En cours', items: [] },
    REVIEW: { id: 'REVIEW', title: 'En révision', items: [] },
    DONE: { id: 'DONE', title: 'Terminé', items: [] }
  })
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [newTaskDescription, setNewTaskDescription] = useState('')
  const [newTaskPriority, setNewTaskPriority] = useState('MEDIUM')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    fetchTasks()
  }, [])

  const fetchTasks = async () => {
    try {
      setLoading(true)
      const response = await api.get('/tasks')
      const tasks = response.data
      
      const newColumns = { ...columns }
      Object.keys(newColumns).forEach(key => {
        newColumns[key].items = tasks.filter(t => t.status === key)
      })
      setColumns(newColumns)
    } catch (error) {
      console.error('Error fetching tasks:', error)
      toast.error('Erreur lors du chargement des tâches')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTask = async () => {
    if (!newTaskTitle.trim()) {
      toast.error('Le titre est requis')
      return
    }
    
    try {
      setSubmitting(true)
      const newTask = await taskService.create({
        title: newTaskTitle,
        description: newTaskDescription,
        priority: newTaskPriority,
        status: 'TODO'
      })
      
      // Ajouter la tâche à la colonne TODO
      const newColumns = { ...columns }
      newColumns.TODO.items = [newTask.task, ...newColumns.TODO.items]
      setColumns(newColumns)
      
      toast.success('Tâche créée avec succès')
      setShowCreateModal(false)
      setNewTaskTitle('')
      setNewTaskDescription('')
      setNewTaskPriority('MEDIUM')
    } catch (error) {
      console.error('Error creating task:', error)
      toast.error(error.response?.data?.error || 'Erreur lors de la création')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDragEnd = async (result) => {
    const { destination, source, draggableId } = result

    if (!destination) return
    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return
    }

    const sourceColumn = columns[source.droppableId]
    const destColumn = columns[destination.droppableId]
    const task = sourceColumn.items[source.index]

    // Mise à jour optimiste
    const newColumns = { ...columns }
    newColumns[source.droppableId].items.splice(source.index, 1)
    newColumns[destination.droppableId].items.splice(destination.index, 0, task)
    setColumns(newColumns)

    // Appel API
    try {
      await api.patch(`/tasks/${task.id}/status`, { status: destination.droppableId })
    } catch (error) {
      console.error('Error updating task status:', error)
      toast.error('Erreur lors de la mise à jour')
      fetchTasks() // Recharger pour corriger
    }
  }

  // Modal de création
  const CreateModal = () => (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowCreateModal(false)}>
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl max-w-md w-full p-6" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            Nouvelle tâche
          </h2>
          <button
            onClick={() => setShowCreateModal(false)}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="label">Titre *</label>
            <input
              type="text"
              value={newTaskTitle}
              onChange={(e) => setNewTaskTitle(e.target.value)}
              className="input"
              placeholder="Titre de la tâche"
              autoFocus
            />
          </div>

          <div>
            <label className="label">Description</label>
            <textarea
              value={newTaskDescription}
              onChange={(e) => setNewTaskDescription(e.target.value)}
              className="input min-h-[80px]"
              placeholder="Description de la tâche"
            />
          </div>

          <div>
            <label className="label">Priorité</label>
            <select
              value={newTaskPriority}
              onChange={(e) => setNewTaskPriority(e.target.value)}
              className="input"
            >
              <option value="LOW">Basse</option>
              <option value="MEDIUM">Moyenne</option>
              <option value="HIGH">Élevée</option>
              <option value="URGENT">Urgent</option>
            </select>
          </div>

          <button
            onClick={handleCreateTask}
            disabled={submitting || !newTaskTitle.trim()}
            className="w-full btn-primary py-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mx-auto"></div>
            ) : (
              'Créer la tâche'
            )}
          </button>
        </div>
      </div>
    </div>
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Tableau Kanban</h1>
          <p className="text-gray-600 dark:text-gray-400">Glissez-déposez pour mettre à jour les statuts</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Nouvelle tâche
        </button>
      </div>

      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.values(columns).map((column) => (
            <div key={column.id} className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-700 dark:text-gray-300">
                  {column.title}
                </h3>
                <span className="text-sm text-gray-500 dark:text-gray-400 bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded-full">
                  {column.items.length}
                </span>
              </div>

              <Droppable droppableId={column.id}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className={`min-h-[200px] transition-colors rounded-lg p-2 ${
                      snapshot.isDraggingOver
                        ? 'bg-gray-200 dark:bg-gray-700'
                        : ''
                    }`}
                  >
                    {column.items.map((task, index) => (
                      <Draggable
                        key={task.id}
                        draggableId={String(task.id)}
                        index={index}
                      >
                        {(provided, snapshot) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            className={`bg-white dark:bg-gray-800 rounded-lg p-4 mb-2 shadow-sm hover:shadow-md transition-shadow ${
                              snapshot.isDragging ? 'shadow-lg rotate-2 scale-105' : ''
                            }`}
                          >
                            <div className="flex items-start justify-between">
                              <h4 className="font-medium text-gray-900 dark:text-white text-sm">
                                {task.title}
                              </h4>
                              <span className={`text-xs px-2 py-1 rounded-full ${
                                task.priority === 'URGENT' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' :
                                task.priority === 'HIGH' ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400' :
                                task.priority === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' :
                                'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                              }`}>
                                {task.priority || 'MEDIUM'}
                              </span>
                            </div>
                            {task.description && (
                              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                                {task.description}
                              </p>
                            )}
                            <div className="flex items-center gap-2 mt-2">
                              {task.assignees?.slice(0, 2).map((assignee) => (
                                <div
                                  key={assignee.id}
                                  className="w-6 h-6 rounded-full bg-indigo-500 flex items-center justify-center text-white text-[10px] font-semibold"
                                >
                                  {assignee.full_name?.charAt(0) || assignee.username?.charAt(0)}
                                </div>
                              ))}
                              {task.assignees?.length > 2 && (
                                <div className="w-6 h-6 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center text-[10px] font-semibold text-gray-700 dark:text-gray-300">
                                  +{task.assignees.length - 2}
                                </div>
                              )}
                              {task.due_date && (
                                <span className="text-[10px] text-gray-500 dark:text-gray-400 ml-auto">
                                  {new Date(task.due_date).toLocaleDateString()}
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </div>
          ))}
        </div>
      </DragDropContext>

      {showCreateModal && <CreateModal />}
    </motion.div>
  )
}

export default TaskBoard
