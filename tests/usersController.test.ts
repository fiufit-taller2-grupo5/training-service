import { UsersController } from '../src/users/usersController';
import { UserCreationParams, UsersService } from 'src/users/usersService';

test('getUser', async () => {
  const mockUSersService: UsersService = {
    get: (id: number, name?: string) => ({
      id,
      email: '',
      name: name ?? '',
      status: 'Sad',
      phoneNumbers: [],
    }),
    create: (userCreationParams: UserCreationParams) => ({
      id: Math.floor(Math.random() * 10000),
      status: 'Sad',
      ...userCreationParams,
    }),
  };

  const usersController = new UsersController(mockUSersService);
  const user = await usersController.getUser(1, 'John Doe');
  expect(user).toEqual({
    id: 1,
    email: '',
    name: 'John Doe',
    status: 'Sad',
    phoneNumbers: [],
  });
});
