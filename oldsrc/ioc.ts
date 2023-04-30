import { IocContainer } from 'tsoa';
import { container } from 'tsyringe';
import { UsersService } from './users/usersService';

container.register('UsersService', { useClass: UsersService });

export const iocContainer: IocContainer = {
  get: <T>(controller: { prototype: T }): T =>
    container.resolve<T>(controller as never),
};
export { container };
export default iocContainer;
