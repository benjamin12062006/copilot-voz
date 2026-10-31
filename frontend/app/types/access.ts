export interface AppUser {
  id: string;
  email: string | null;
  displayName: string | null;
  createdAt: string;
  updatedAt: string;
}

export type AccessStage =
  'configuration' | 'restore' | 'login' | 'profile' | 'logout';

export type AccessState =
  | { status: 'checking' }
  | { status: 'signedOut'; notice?: string }
  | { status: 'authenticating'; attempt: number }
  | { status: 'preparingProfile' }
  | { status: 'ready'; user: AppUser }
  | { status: 'signingOut' }
  | { status: 'error'; stage: AccessStage; message: string };

export class AccessFailure extends Error {
  constructor(
    message: string,
    public readonly kind:
      | 'unauthenticated'
      | 'notFound'
      | 'network'
      | 'configuration'
      | 'forbidden',
  ) {
    super(message);
    this.name = 'AccessFailure';
  }
}

export interface SessionService {
  restore(): Promise<boolean>;
  token(forceRefresh?: boolean): Promise<string>;
  signOut(): Promise<void>;
}

export interface ProfileService {
  read(): Promise<AppUser>;
  provision(): Promise<AppUser>;
}
