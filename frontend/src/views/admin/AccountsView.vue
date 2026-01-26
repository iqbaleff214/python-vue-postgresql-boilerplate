<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import AppLayout from "@/components/AppLayout.vue"
import { useAuthStore } from "@/stores/auth"
import { accountsService } from "@/services/accounts"
import type { CreateAccountPayload } from "@/services/accounts"
import type { User } from "@/services/auth"
import UserAvatar from "@/components/UserAvatar.vue"

const auth = useAuthStore()
const accounts = ref<User[]>([])
const loading = ref(false)
const error = ref("")

const showCreateModal = ref(false)
const createLoading = ref(false)
const createError = ref("")
const createForm = ref<CreateAccountPayload>({
  name: "",
  email: "",
  phone_number: "",
  password: "",
  role: "USER",
})

const deleteTarget = ref<User | null>(null)
const deleteLoading = ref(false)

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

function roleBadgeClass(role: string) {
  switch (role) {
    case "ADMIN":
      return "bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-400"
    case "STAFF":
      return "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
    default:
      return "bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300"
  }
}

const canDelete = computed(() => (account: User) => account.id !== auth.user?.id)

async function fetchAccounts() {
  loading.value = true
  error.value = ""
  try {
    accounts.value = await accountsService.list()
  } catch {
    error.value = "Failed to load accounts."
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  createForm.value = { name: "", email: "", phone_number: "", password: "", role: "USER" }
  createError.value = ""
  showCreateModal.value = true
}

async function handleCreate() {
  createLoading.value = true
  createError.value = ""
  try {
    await accountsService.create(createForm.value)
    showCreateModal.value = false
    await fetchAccounts()
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    createError.value = err.response?.data?.detail || "Failed to create account."
  } finally {
    createLoading.value = false
  }
}

function openDeleteModal(account: User) {
  deleteTarget.value = account
}

async function handleDelete() {
  if (!deleteTarget.value) return
  deleteLoading.value = true
  try {
    await accountsService.remove(deleteTarget.value.id)
    deleteTarget.value = null
    await fetchAccounts()
  } catch {
    // silently close
  } finally {
    deleteLoading.value = false
  }
}

onMounted(fetchAccounts)
</script>

<template>
  <AppLayout>
    <div>
      <div class="mb-6 flex items-center justify-between">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Accounts</h1>
        <button
          class="rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
          @click="openCreateModal"
        >
          Create account
        </button>
      </div>

      <div v-if="error" class="mb-4 rounded-lg bg-red-50 p-4 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
        {{ error }}
      </div>

      <div v-if="loading" class="py-12 text-center text-gray-500 dark:text-gray-400">Loading...</div>

      <div v-else class="overflow-hidden rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-900/50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">User</th>
                <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">Email</th>
                <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">Phone</th>
                <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">Role</th>
                <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">Created</th>
                <th class="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">Updated</th>
                <th class="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="account in accounts" :key="account.id">
                <td class="whitespace-nowrap px-6 py-4">
                  <div class="flex items-center gap-3">
                    <UserAvatar :name="account.name" :avatar-url="account.avatar_url" size="sm" />
                    <div class="text-sm font-medium text-gray-900 dark:text-white">
                      {{ account.name }}<span v-if="account.surname">&nbsp;{{ account.surname }}</span>
                    </div>
                  </div>
                </td>
                <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{{ account.email }}</td>
                <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{{ account.phone_number }}</td>
                <td class="whitespace-nowrap px-6 py-4">
                  <span
                    class="inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium"
                    :class="roleBadgeClass(account.role)"
                  >
                    {{ account.role }}
                  </span>
                </td>
                <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{{ formatDate(account.created_at) }}</td>
                <td class="whitespace-nowrap px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{{ formatDate(account.updated_at) }}</td>
                <td class="whitespace-nowrap px-6 py-4 text-right">
                  <button
                    v-if="canDelete(account)"
                    class="text-sm font-medium text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                    @click="openDeleteModal(account)"
                  >
                    Delete
                  </button>
                </td>
              </tr>
              <tr v-if="accounts.length === 0">
                <td colspan="7" class="px-6 py-8 text-center text-sm text-gray-500 dark:text-gray-400">No accounts found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <Teleport to="body">
      <div v-if="showCreateModal" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="fixed inset-0 bg-black/50" @click="showCreateModal = false" />
        <div class="relative z-10 w-full max-w-md rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800">
          <h2 class="mb-4 text-lg font-semibold text-gray-900 dark:text-white">Create account</h2>

          <div v-if="createError" class="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
            {{ createError }}
          </div>

          <form class="space-y-4" @submit.prevent="handleCreate">
            <div>
              <label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">Name</label>
              <input
                v-model="createForm.name"
                type="text"
                required
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">Surname</label>
              <input
                v-model="createForm.surname"
                type="text"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
              <input
                v-model="createForm.email"
                type="email"
                required
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">Phone number</label>
              <input
                v-model="createForm.phone_number"
                type="text"
                required
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
              <input
                v-model="createForm.password"
                type="password"
                required
                minlength="6"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300">Role</label>
              <select
                v-model="createForm.role"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              >
                <option value="USER">User</option>
                <option value="STAFF">Staff</option>
                <option value="ADMIN">Admin</option>
              </select>
            </div>
            <div class="flex justify-end gap-3 pt-2">
              <button
                type="button"
                class="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
                @click="showCreateModal = false"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="createLoading"
                class="rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-50"
              >
                {{ createLoading ? "Creating..." : "Create" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Delete Confirmation Modal -->
    <Teleport to="body">
      <div v-if="deleteTarget" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="fixed inset-0 bg-black/50" @click="deleteTarget = null" />
        <div class="relative z-10 w-full max-w-sm rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800">
          <h2 class="mb-2 text-lg font-semibold text-gray-900 dark:text-white">Delete account</h2>
          <p class="mb-4 text-sm text-gray-600 dark:text-gray-400">
            Are you sure you want to delete
            <span class="font-medium text-gray-900 dark:text-white">{{ deleteTarget.name }}</span>
            ({{ deleteTarget.email }})? This action cannot be undone.
          </p>
          <div class="flex justify-end gap-3">
            <button
              type="button"
              class="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
              @click="deleteTarget = null"
            >
              Cancel
            </button>
            <button
              type="button"
              :disabled="deleteLoading"
              class="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
              @click="handleDelete"
            >
              {{ deleteLoading ? "Deleting..." : "Delete" }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </AppLayout>
</template>
