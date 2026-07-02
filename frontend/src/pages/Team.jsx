import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Users, 
  UserPlus, 
  Mail, 
  Crown,
  UserMinus,
  Shield,
  User,
  X
} from 'lucide-react'
import api from '../services/api'
import toast from 'react-hot-toast'

const Team = () => {
  const [team, setTeam] = useState(null)
  const [members, setMembers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showInviteModal, setShowInviteModal] = useState(false)
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState('member')
  const [submitting, setSubmitting] = useState(false)
  const [userInfo, setUserInfo] = useState(null)

  useEffect(() => {
    fetchTeamData()
    fetchUserInfo()
  }, [])

  const fetchUserInfo = async () => {
    try {
      const response = await api.get('/auth/me')
      setUserInfo(response.data)
    } catch (error) {
      console.error('Error fetching user info:', error)
    }
  }

  const fetchTeamData = async () => {
    try {
      setLoading(true)
      const [teamRes, membersRes] = await Promise.all([
        api.get('/team'),
        api.get('/team/members')
      ])
      setTeam(teamRes.data)
      setMembers(membersRes.data)
    } catch (error) {
      console.error('Error fetching team data:', error)
      // Si l'utilisateur n'a pas d'équipe, on l'ignore
      if (error.response?.status !== 404) {
        toast.error('Erreur lors du chargement de l\'équipe')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleInvite = async (e) => {
    e.preventDefault()
    
    if (!inviteEmail.trim()) {
      toast.error('Veuillez entrer une adresse email')
      return
    }
    
    try {
      setSubmitting(true)
      const response = await api.post('/team/invite', {
        email: inviteEmail,
        role: inviteRole
      })
      toast.success('Invitation envoyée avec succès !')
      setInviteEmail('')
      setShowInviteModal(false)
      // Rafraîchir les données
      fetchTeamData()
    } catch (error) {
      console.error('Error sending invite:', error)
      const errorMsg = error.response?.data?.error || 'Erreur lors de l\'invitation'
      toast.error(errorMsg)
    } finally {
      setSubmitting(false)
    }
  }

  const handleRemoveMember = async (userId) => {
    if (!confirm('Êtes-vous sûr de vouloir retirer ce membre ?')) return
    try {
      await api.delete(`/team/members/${userId}`)
      toast.success('Membre retiré avec succès')
      fetchTeamData()
    } catch (error) {
      console.error('Error removing member:', error)
      toast.error(error.response?.data?.error || 'Erreur lors du retrait du membre')
    }
  }

  const handleUpdateRole = async (userId, role) => {
    try {
      await api.patch(`/team/members/${userId}/role`, { role })
      toast.success('Rôle mis à jour avec succès')
      fetchTeamData()
    } catch (error) {
      console.error('Error updating role:', error)
      toast.error(error.response?.data?.error || 'Erreur lors de la mise à jour du rôle')
    }
  }

  const getRoleBadge = (role) => {
    const colors = {
      admin: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
      manager: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
      member: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-400'
    }
    const icons = {
      admin: <Crown className="w-4 h-4" />,
      manager: <Shield className="w-4 h-4" />,
      member: <User className="w-4 h-4" />
    }
    return (
      <span className={`flex items-center gap-1 text-xs px-2 py-1 rounded-full ${colors[role] || colors.member}`}>
        {icons[role] || icons.member}
        {role.charAt(0).toUpperCase() + role.slice(1)}
      </span>
    )
  }

  const getInitials = (name) => {
    if (!name) return 'U'
    const parts = name.split(' ')
    if (parts.length >= 2) {
      return parts[0].charAt(0) + parts[1].charAt(0)
    }
    return name.charAt(0).toUpperCase()
  }

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
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Équipe</h1>
          <p className="text-gray-600 dark:text-gray-400">
            {team?.name || 'Votre équipe'} • {members.length} membres
          </p>
        </div>
        <button
          onClick={() => setShowInviteModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <UserPlus className="w-5 h-5" />
          Inviter un membre
        </button>
      </div>

      {/* Team Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <Users className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{members.length}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Membres</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
              <Crown className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {members.filter(m => m.role === 'admin').length}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Admins</p>
            </div>
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
              <UserPlus className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {members.filter(m => m.role === 'member').length}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">Membres</p>
            </div>
          </div>
        </div>
      </div>

      {/* Members List */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Membre
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Rôle
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Rejoint le
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {members.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                    Aucun membre dans l'équipe
                  </td>
                </tr>
              ) : (
                members.map((member) => (
                  <tr key={member.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-indigo-500 flex items-center justify-center text-white font-semibold text-sm">
                          {getInitials(member.user?.full_name || member.user?.username)}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900 dark:text-white">
                            {member.user?.full_name || member.user?.username || 'Utilisateur'}
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            @{member.user?.username || 'unknown'}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-300">
                      {member.user?.email || 'N/A'}
                    </td>
                    <td className="px-6 py-4">
                      {getRoleBadge(member.role)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                      {member.joined_at ? new Date(member.joined_at).toLocaleDateString('fr-FR', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric'
                      }) : '-'}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <select
                          value={member.role}
                          onChange={(e) => handleUpdateRole(member.user.id, e.target.value)}
                          className="text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-2 py-1 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          <option value="member">Membre</option>
                          <option value="manager">Manager</option>
                          <option value="admin">Admin</option>
                        </select>
                        {member.user?.id !== userInfo?.id && (
                          <button
                            onClick={() => handleRemoveMember(member.user.id)}
                            className="p-1 hover:bg-red-100 dark:hover:bg-red-900/30 rounded transition-colors"
                          >
                            <UserMinus className="w-4 h-4 text-red-500" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowInviteModal(false)}>
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl max-w-md w-full p-6" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                Inviter un membre
              </h2>
              <button
                onClick={() => setShowInviteModal(false)}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <form onSubmit={handleInvite} className="space-y-4">
              <div>
                <label className="label">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="email"
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    className="input pl-10"
                    placeholder="email@exemple.com"
                    required
                    autoFocus
                  />
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  L'utilisateur recevra un email d'invitation
                </p>
              </div>

              <div>
                <label className="label">Rôle</label>
                <select
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value)}
                  className="input"
                >
                  <option value="member">Membre</option>
                  <option value="manager">Manager</option>
                  <option value="admin">Admin</option>
                </select>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Les admins peuvent gérer l'équipe et les tâches
                </p>
              </div>

              <button
                type="submit"
                disabled={submitting || !inviteEmail.trim()}
                className="w-full btn-primary py-3 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {submitting ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                ) : (
                  <>
                    <Mail className="w-4 h-4" />
                    Envoyer l'invitation
                  </>
                )}
              </button>
            </form>
          </div>
        </div>
      )}
    </motion.div>
  )
}

export default Team