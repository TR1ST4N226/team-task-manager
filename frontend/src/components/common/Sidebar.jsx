import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { 
  LayoutDashboard, 
  ListTodo, 
  Kanban, 
  Users, 
  BarChart3,
  Settings 
} from 'lucide-react'
import toast from 'react-hot-toast'

const Sidebar = () => {
  const navigate = useNavigate()

  const menuItems = [
    { path: '/', icon: LayoutDashboard, label: 'Tableau de bord' },
    { path: '/tasks', icon: ListTodo, label: 'Tâches' },
    { path: '/board', icon: Kanban, label: 'Kanban' },
    { path: '/team', icon: Users, label: 'Équipe' },
    { path: '/analytics', icon: BarChart3, label: 'Analytiques' },
  ]

  const handleSettings = () => {
    toast.info('⚙️ Paramètres en cours de développement', {
      duration: 3000,
      style: {
        background: '#4F46E5',
        color: '#fff',
      },
    })
  }

  return (
    <aside className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex-shrink-0 hidden md:block">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
          TeamTask
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Gestion de projets
        </p>
      </div>

      <nav className="px-4 space-y-1">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900/20 dark:text-indigo-400'
                  : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700'
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="absolute bottom-0 w-64 p-4 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={handleSettings}
          className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700 transition-colors w-full"
        >
          <Settings className="w-5 h-5" />
          <span className="font-medium">Paramètres</span>
        </button>
      </div>
    </aside>
  )
}

export default Sidebar